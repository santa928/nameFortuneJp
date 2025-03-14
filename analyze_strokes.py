import asyncio
import logging
from fortune_analyzer import FortuneAnalyzer
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def progress_handler(progress: float, pattern: List[int]):
    """進捗状況をログ出力"""
    logger.info(f"進捗: {progress:.1f}% - 現在の画数: {pattern}")

async def main():
    analyzer = FortuneAnalyzer()
    
    # 1文字、2文字、3文字のパターンを順番に分析
    for char_count in range(1, 4):
        logger.info(f"{char_count}文字の分析を開始します")
        
        results = await analyzer.analyze(
            char_count=char_count,
            progress_callback=progress_handler
        )
        
        # 結果を保存
        filename = await analyzer.save_results(results)
        logger.info(f"{char_count}文字の分析結果を {filename} に保存しました")
        
        # 上位10件の結果を表示
        logger.info(f"\n=== {char_count}文字の上位10件 ===")
        for i, result in enumerate(results["top_results"], 1):
            logger.info(f"{i}位: 画数{result['strokes']} - 文字列「{result['characters']}」")
            logger.info(f"  enamae: {result['enamae_result']}")
            logger.info(f"  namaeuranai: {result['namaeuranai_result']}")
            logger.info(f"  総合スコア: {result['total_score']}\n")

if __name__ == "__main__":
    asyncio.run(main()) 