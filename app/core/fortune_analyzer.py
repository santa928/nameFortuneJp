import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
from app.core.scraper import create_scraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProgressTracker:
    """進捗状況を追跡するクラス"""
    
    def __init__(self, total_patterns: int):
        self.total_patterns = total_patterns
        self.current = 0
        
    def update(self, pattern: List[int]) -> float:
        """進捗を更新し、現在の進捗率を返す

        Args:
            pattern (List[int]): 現在処理中の画数パターン

        Returns:
            float: 進捗率（0-100）
        """
        self.current += 1
        return (self.current / self.total_patterns) * 100

class StrokePatternGenerator:
    """画数パターンを生成するクラス"""
    
    def generate_patterns(self, char_count: int) -> List[List[int]]:
        """文字数に応じた画数パターンを生成

        Args:
            char_count (int): 文字数（1-3）

        Returns:
            List[List[int]]: 画数パターンのリスト
        """
        if char_count == 1:
            return [[i] for i in range(1, 21)]
        elif char_count == 2:
            return [[i, j] for i in range(1, 21) for j in range(1, 21)]
        else:  # char_count == 3
            return [[i, j, k] for i in range(1, 21) 
                              for j in range(1, 21) 
                              for k in range(1, 21)]

class FortuneAnalyzer:
    """運勢分析クラス"""
    
    def __init__(self):
        self.scraper = create_scraper()
        self.pattern_generator = StrokePatternGenerator()
        
    async def analyze(self, last_name: str, char_count: int, progress_callback=None) -> Dict[str, Any]:
        """指定された文字数の画数パターンを分析

        Args:
            last_name (str): 名字
            char_count (int): 文字数（1-3）
            progress_callback (callable, optional): 進捗報告用コールバック関数

        Returns:
            Dict[str, Any]: 分析結果
        """
        patterns = self.pattern_generator.generate_patterns(char_count)
        progress = ProgressTracker(len(patterns))
        results = []
        
        async def process_pattern(pattern: List[int]) -> Dict[str, Any]:
            await asyncio.sleep(0.5)  # 0.5秒のウェイト
            name = "".join([get_character_by_strokes(s) for s in pattern])
            fortune_result = self.scraper.get_fortune(last_name, name, "m", stroke_list_mode=True)
            
            if progress_callback:
                progress_rate = progress.update(pattern)
                await progress_callback(progress_rate, pattern)

            # スコア計算のデバッグログを追加
            enamae_score = self._calculate_enamae_score(fortune_result["enamae"])
            namaeuranai_score = self._calculate_namaeuranai_score(fortune_result["namaeuranai"])
            total_score = (enamae_score + namaeuranai_score) / 2
            
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
                "total_score": total_score
            }
            
        # 4並列で実行
        semaphore = asyncio.Semaphore(4)
        tasks = []
        for pattern in patterns:
            async with semaphore:
                tasks.append(process_pattern(pattern))
                
        results = await asyncio.gather(*tasks)
        
        # スコアで降順ソートして上位20件を取得
        sorted_results = sorted(results, key=lambda x: x["total_score"], reverse=True)[:20]
        
        return {
            "generated_at": datetime.now().isoformat(),
            "last_name": last_name,
            "char_count": char_count,
            "total_patterns": len(patterns),
            "top_results": sorted_results
        }
        
    def _calculate_total_score(self, fortune_result: Dict[str, Any]) -> float:
        """運勢結果からトータルスコアを計算

        Args:
            fortune_result (Dict[str, Any]): 運勢結果

        Returns:
            float: トータルスコア
        """
        enamae_score = self._calculate_enamae_score(fortune_result["enamae"])
        namaeuranai_score = self._calculate_namaeuranai_score(fortune_result["namaeuranai"])
        return (enamae_score + namaeuranai_score) / 2
        
    def _calculate_enamae_score(self, result: Dict[str, str]) -> float:
        """enamae.netの結果からスコアを計算"""
        score_map = {
            "大吉": 100,
            "吉": 80,
            "特殊格": 90,
            "吉凶混合": 60,
            "凶": 40,
            "大凶": 20
        }
        
        scores = []
        target_keys = ["天格", "人格", "地格", "外格", "総格", "三才配置"]
        
        # 基本運勢のスコア計算
        for key in target_keys:
            if key in result:
                value = result[key]
                score = score_map.get(value, 0)
                if score == 0:
                    logger.warning(f"enamae: {key}の値「{value}」のスコアが0になりました")
                scores.append(score)
            
        logger.debug(f"enamae raw result: {result}")
        logger.debug(f"enamae scores: {list(zip(target_keys, scores))}")
        return sum(scores) / len(scores) if scores else 0
        
    def _calculate_namaeuranai_score(self, result: Dict[str, str]) -> float:
        """namaeuranai.bizの結果からスコアを計算"""
        score_map = {
            "大大吉": 100,
            "大吉": 90,
            "吉": 80,
            "凶": 40,
            "大凶": 20
        }
        
        scores = []
        target_keys = ["天格", "人格", "地格", "外格", "総格", "仕事運", "家庭運"]
        
        # 基本運勢のスコア計算
        for key in target_keys:
            if key in result:
                value = result[key]
                score = score_map.get(value, 0)
                if score == 0:
                    logger.warning(f"namaeuranai: {key}の値「{value}」のスコアが0になりました")
                scores.append(score)
            
        logger.debug(f"namaeuranai raw result: {result}")
        logger.debug(f"namaeuranai scores: {list(zip(target_keys, scores))}")
        return sum(scores) / len(scores) if scores else 0

    async def save_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """分析結果をJSONファイルに保存

        Args:
            results (Dict[str, Any]): 分析結果
            filename (str, optional): 保存するファイル名

        Returns:
            str: 保存したファイルのパス
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fortune_analysis_{timestamp}.json"
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        return filename

def get_character_by_strokes(strokes: int) -> str:
    """画数に対応する文字を返す

    Args:
        strokes (int): 画数（1-20）

    Returns:
        str: 対応する漢字
    """
    stroke_characters = {
        1: '一', 2: '二', 3: '三', 4: '中', 5: '兄',
        6: '両', 7: '乱', 8: '並', 9: '乗', 10: '俺',
        11: '停', 12: '博', 13: '働', 14: '僕', 15: '劇',
        16: '疑', 17: '優', 18: '儲', 19: '爆', 20: '競'
    }
    return stroke_characters.get(strokes, '一') 