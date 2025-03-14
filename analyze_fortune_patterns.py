import json
from scraper import create_scraper
import logging
from collections import defaultdict
import time
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_character_by_strokes(strokes):
    # 画数に対応する文字を返す
    stroke_characters = {
        1: '一', 2: '二', 3: '三', 4: '中', 5: '兄',
        6: '両', 7: '乱', 8: '並', 9: '乗', 10: '俺',
        11: '停', 12: '博', 13: '働', 14: '僕', 15: '劇',
        16: '疑', 17: '優', 18: '儲', 19: '爆', 20: '競'
    }
    return stroke_characters.get(strokes, '一')

def analyze_fortune_patterns():
    """運勢パターンを分析"""
    scraper = create_scraper()
    results = {
        'm': defaultdict(list),
        'f': defaultdict(list)
    }
    
    # 共通項目とサイト固有の項目を定義
    common_keys = ["天格", "人格", "地格", "外格", "総格"]
    enamae_keys = ["三才配置", "陰陽配列"]
    namaeuranai_keys = ["仕事運", "家庭運"]
    
    # 1画の名前でテスト
    test_strokes = 1
    test_name = get_character_by_strokes(test_strokes)
    logger.info(f"分析中: 田中{test_name} ({test_strokes}画)")
    test_result = scraper.get_fortune("田中", test_name, 'm')
    
    if "error" in test_result:
        logger.error(f"運用チェックでエラーが発生: {test_result['error']}")
        return
    
    if not test_result["enamae"] and not test_result["namaeuranai"]:
        logger.error("運用チェック: 両サイトからデータを取得できませんでした")
        return

    # 全ての画数で分析
    for gender in ['m', 'f']:
        logger.info(f"=== {'男性' if gender == 'm' else '女性'}の分析を開始 ===")
        
        for strokes in range(1, 21):
            character = get_character_by_strokes(strokes)
            logger.info(f"分析中: 田中{character} ({strokes}画)")
            
            fortune_result = scraper.get_fortune("田中", character, gender)
            if "error" in fortune_result:
                logger.error(f"エラー発生: {fortune_result['error']}")
                continue
            
            # enamae.netの結果を処理
            if fortune_result["enamae"]:
                for key, value in fortune_result["enamae"].items():
                    if not key.endswith("_説明"):
                        results[gender][f"enamae_{key}"].append(value)
            else:
                logger.warning(f"enamae.netからデータを取得できませんでした: 田中{character}")
            
            # namaeuranai.bizの結果を処理
            if fortune_result["namaeuranai"]:
                for key, value in fortune_result["namaeuranai"].items():
                    if not key.endswith("_説明"):
                        results[gender][f"namaeuranai_{key}"].append(value)
            else:
                logger.warning(f"namaeuranai.bizからデータを取得できませんでした: 田中{character}")
            
            time.sleep(1)  # サーバー負荷軽減のため1秒待機

    logger.info("分析が完了しました")
    return results

if __name__ == '__main__':
    analyze_fortune_patterns() 