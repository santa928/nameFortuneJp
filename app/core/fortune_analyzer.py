import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from app.core.scraper import create_scraper

# 中央の setup_logging() で basicConfig が呼び出される
logger = logging.getLogger(__name__)


class ProgressTracker:
    """進捗状況を追跡するクラス"""

    def __init__(self, total_patterns: int):
        self.total_patterns = total_patterns
        self.current = 0

    def update(self, pattern: List[int]) -> float:
        self.current += 1
        return (self.current / self.total_patterns) * 100


class StrokePatternGenerator:
    """画数パターンを生成するクラス"""

    def generate_patterns(self, char_count: int) -> List[List[int]]:
        if char_count == 1:
            return [[i] for i in range(1, 21)]
        elif char_count == 2:
            return [[i, j] for i in range(1, 21) for j in range(1, 21)]
        else:
            return [
                [i, j, k]
                for i in range(1, 21)
                for j in range(1, 21)
                for k in range(1, 21)
            ]


class FortuneAnalyzer:
    """運勢分析クラス"""

    def __init__(self) -> None:
        self.scraper = create_scraper()
        self.pattern_generator = StrokePatternGenerator()

    async def analyze(
        self,
        last_name: str,
        char_count: int,
        progress_callback: Optional[Callable[[float, List[int]], Any]] = None,
    ) -> Dict[str, Any]:
        patterns = self.pattern_generator.generate_patterns(char_count)
        progress = ProgressTracker(len(patterns))

        async def process_pattern(pattern: List[int]) -> Dict[str, Any]:
            await asyncio.sleep(0.5)
            name = "".join([get_character_by_strokes(s) for s in pattern])
            raw_fortune_result = await asyncio.to_thread(
                self.scraper.get_fortune, last_name, name, "m", True
            )

            fortune_result = {
                "enamae": raw_fortune_result.get("enamae.net", {}),
                "namaeuranai": raw_fortune_result.get("namaeuranai.biz", {}),
            }

            if progress_callback:
                progress_rate = progress.update(pattern)
                await progress_callback(progress_rate, pattern)

            enamae_score, namaeuranai_score, total_score = self._calculate_scores(
                fortune_result
            )

            logger.debug(f"Pattern {pattern} ({name}):")
            logger.debug(f"enamae result: {fortune_result['enamae']}")
            logger.debug(f"enamae score: {enamae_score}")
            logger.debug(f"namaeuranai result: {fortune_result['namaeuranai']}")
            logger.debug(f"namaeuranai score: {namaeuranai_score}")
            logger.debug(f"total score: {total_score}")

            return {
                "strokes": pattern,
                "characters": name,
                "enamae_result": fortune_result["enamae"],
                "namaeuranai_result": fortune_result["namaeuranai"],
                "total_score": total_score,
                "has_provider_result": bool(
                    fortune_result["enamae"] or fortune_result["namaeuranai"]
                ),
            }

        semaphore = asyncio.Semaphore(4)

        async def _sem_task(pattern: List[int]) -> Dict[str, Any]:
            async with semaphore:
                return await process_pattern(pattern)

        tasks = [asyncio.create_task(_sem_task(pattern)) for pattern in patterns]
        results = await asyncio.gather(*tasks)

        # 両プロバイダーが取得不能だったパターンはランキング対象から除外する。
        valid_results = [result for result in results if result.pop("has_provider_result")]
        sorted_results = sorted(
            valid_results, key=lambda x: x["total_score"], reverse=True
        )[:20]

        return {
            "generated_at": datetime.now().isoformat(),
            "last_name": last_name,
            "char_count": char_count,
            "total_patterns": len(patterns),
            "top_results": sorted_results,
        }

    def _calculate_total_score(self, fortune_result: Dict[str, Any]) -> float:
        _, _, total_score = self._calculate_scores(fortune_result)
        return total_score

    def _calculate_scores(
        self, fortune_result: Dict[str, Any]
    ) -> tuple[float, float, float]:
        """取得できたプロバイダーだけを使ってスコアを計算する。"""
        enamae_result = fortune_result.get("enamae", {})
        namaeuranai_result = fortune_result.get("namaeuranai", {})
        enamae_score = self._calculate_enamae_score(enamae_result)
        namaeuranai_score = self._calculate_namaeuranai_score(namaeuranai_result)

        available_scores = []
        if enamae_result:
            available_scores.append(enamae_score)
        if namaeuranai_result:
            available_scores.append(namaeuranai_score)

        total_score = (
            sum(available_scores) / len(available_scores) if available_scores else 0
        )
        return enamae_score, namaeuranai_score, total_score

    def _calculate_enamae_score(self, result: Dict[str, str]) -> float:
        score_map = {
            "大吉": 100,
            "吉": 80,
            "特殊格": 90,
            "吉凶混合": 60,
            "凶": 40,
            "大凶": 20,
        }
        scores = []
        target_keys = ["天格", "人格", "地格", "外格", "総格", "三才配置"]
        for key in target_keys:
            if key in result:
                value = result[key]
                score = score_map.get(value, 0)
                if score == 0:
                    logger.warning(
                        f"enamae: {key}の値「{value}」のスコアが0になりました"
                    )
                scores.append(score)
        logger.debug(f"enamae raw result: {result}")
        logger.debug(f"enamae scores: {list(zip(target_keys, scores))}")
        return sum(scores) / len(scores) if scores else 0

    def _calculate_namaeuranai_score(self, result: Dict[str, str]) -> float:
        score_map = {"大大吉": 100, "大吉": 90, "吉": 80, "凶": 40, "大凶": 20}
        scores = []
        target_keys = ["天格", "人格", "地格", "外格", "総格", "仕事運", "家庭運"]
        for key in target_keys:
            if key in result:
                value = result[key]
                score = score_map.get(value, 0)
                if score == 0:
                    logger.warning(
                        f"namaeuranai: {key}の値「{value}」のスコアが0になりました"
                    )
                scores.append(score)
        logger.debug(f"namaeuranai raw result: {result}")
        logger.debug(f"namaeuranai scores: {list(zip(target_keys, scores))}")
        return sum(scores) / len(scores) if scores else 0

    async def save_results(
        self, results: Dict[str, Any], filename: Optional[str] = None
    ) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fortune_analysis_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        return filename


def get_character_by_strokes(strokes: int) -> str:
    stroke_characters = {
        1: "一",
        2: "二",
        3: "三",
        4: "中",
        5: "兄",
        6: "両",
        7: "乱",
        8: "並",
        9: "乗",
        10: "俺",
        11: "停",
        12: "博",
        13: "働",
        14: "僕",
        15: "劇",
        16: "壊",
        17: "優",
        18: "儲",
        19: "爆",
        20: "競",
    }
    return stroke_characters.get(strokes, "一")
