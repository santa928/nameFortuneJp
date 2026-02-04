import asyncio
import logging
import os
import threading
from typing import Any, Dict, List

from app.core.fortune_analyzer import FortuneAnalyzer

logger = logging.getLogger(__name__)


class AnalysisProgressStore:
    """進捗情報の保存と取得を担当するクラス"""

    def __init__(self) -> None:
        self._progress: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def init(self, queue_id: str) -> None:
        self._set(queue_id, {"progress": 0, "status": "running"})

    def update(self, queue_id: str, progress_rate: float, pattern: List[int]) -> None:
        self._set(
            queue_id,
            {"progress": progress_rate, "status": "running", "pattern": pattern},
        )

    def complete(self, queue_id: str, results: Dict[str, Any]) -> None:
        self._set(queue_id, {"progress": 100, "status": "complete", "results": results})

    def error(self, queue_id: str, error: str) -> None:
        self._set(queue_id, {"progress": -1, "status": "error", "error": error})

    def get(self, queue_id: str) -> Dict[str, Any]:
        with self._lock:
            return dict(self._progress.get(queue_id, {}))

    def _set(self, queue_id: str, value: Dict[str, Any]) -> None:
        with self._lock:
            self._progress[queue_id] = value


class StrokeAnalysisService:
    """画数パターン分析の実行を担当するクラス"""

    def __init__(self, progress_store: AnalysisProgressStore) -> None:
        self._progress_store = progress_store

    def start_analysis(self, last_name: str, char_count: int) -> str:
        queue_id = self._build_queue_id(last_name, char_count)
        self._progress_store.init(queue_id)

        thread = threading.Thread(
            target=self._run_analysis_thread,
            args=(queue_id, last_name, char_count),
            daemon=True,
        )
        thread.start()

        return queue_id

    def _build_queue_id(self, last_name: str, char_count: int) -> str:
        return f"{last_name}_{char_count}"

    def _build_result_filename(self, last_name: str, char_count: int) -> str:
        return f"static/results_{last_name}_{char_count}字.json"

    def _run_analysis_thread(
        self, queue_id: str, last_name: str, char_count: int
    ) -> None:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                self._analyze(
                    queue_id=queue_id, last_name=last_name, char_count=char_count
                )
            )
        except Exception as e:
            logger.exception("分析スレッドでエラーが発生しました")
            self._progress_store.error(queue_id, str(e))
        finally:
            try:
                loop.close()
            except Exception:
                logger.exception("イベントループのクローズに失敗しました")

    async def _analyze(self, queue_id: str, last_name: str, char_count: int) -> None:
        try:
            analyzer = FortuneAnalyzer()

            async def progress_callback(
                progress_rate: float, pattern: List[int]
            ) -> None:
                self._progress_store.update(queue_id, progress_rate, pattern)
                logger.debug(
                    "Progress for %s: %s%%, Pattern: %s",
                    queue_id,
                    progress_rate,
                    pattern,
                )

            results = await analyzer.analyze(
                last_name=last_name,
                char_count=char_count,
                progress_callback=progress_callback,
            )

            filename = self._build_result_filename(last_name, char_count)
            os.makedirs("static", exist_ok=True)
            await analyzer.save_results(results, filename)

            self._progress_store.complete(queue_id, results)

        except Exception as e:
            logger.exception("分析処理中にエラーが発生しました")
            self._progress_store.error(queue_id, str(e))
