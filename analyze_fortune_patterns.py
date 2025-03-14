import json
from scraper import create_scraper
import logging
from collections import defaultdict
import time
import matplotlib.pyplot as plt
import pandas as pd
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

def create_graphs(results, output_dir):
    """運勢パターンのグラフを生成"""
    os.makedirs(output_dir, exist_ok=True)
    
    for gender in ['m', 'f']:
        gender_name = '男性' if gender == 'm' else '女性'
        
        # 共通項目のグラフ
        common_keys = ["天格", "人格", "地格", "外格", "総格"]
        for key in common_keys:
            plt.figure(figsize=(10, 6))
            values = results[gender][f"enamae_{key}"]
            unique_values = list(set(values))
            counts = [values.count(v) for v in unique_values]
            
            plt.pie(counts, labels=unique_values, autopct='%1.1f%%')
            plt.title(f'{gender_name}の{key}の分布')
            plt.savefig(os.path.join(output_dir, f'{gender}_{key}_pie.png'))
            plt.close()

def create_html_report(results, output_dir):
    """HTMLレポートを生成"""
    os.makedirs(output_dir, exist_ok=True)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>姓名判断分析レポート</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .section { margin-bottom: 30px; }
            .graph { text-align: center; margin: 20px 0; }
            table { border-collapse: collapse; width: 100%; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>姓名判断分析レポート</h1>
            <p>生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """
    
    for gender in ['m', 'f']:
        gender_name = '男性' if gender == 'm' else '女性'
        html_content += f"""
            <div class="section">
                <h2>{gender_name}の分析結果</h2>
        """
        
        # 共通項目の結果
        common_keys = ["天格", "人格", "地格", "外格", "総格"]
        for key in common_keys:
            html_content += f"""
                <h3>{key}</h3>
                <div class="graph">
                    <img src="{gender}_{key}_pie.png" alt="{key}の分布">
                </div>
                <table>
                    <tr><th>運勢</th><th>回数</th><th>割合</th></tr>
            """
            
            values = results[gender][f"enamae_{key}"]
            unique_values = list(set(values))
            for value in unique_values:
                count = values.count(value)
                percentage = (count / len(values)) * 100
                html_content += f"""
                    <tr>
                        <td>{value}</td>
                        <td>{count}</td>
                        <td>{percentage:.1f}%</td>
                    </tr>
                """
            
            html_content += "</table>"
        
        html_content += "</div>"
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(output_dir, 'report.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

def export_to_csv(results, output_dir):
    """結果をCSVファイルにエクスポート"""
    os.makedirs(output_dir, exist_ok=True)
    
    for gender in ['m', 'f']:
        gender_name = '男性' if gender == 'm' else '女性'
        data = []
        
        for key, values in results[gender].items():
            unique_values = list(set(values))
            for value in unique_values:
                count = values.count(value)
                percentage = (count / len(values)) * 100
                data.append({
                    '項目': key,
                    '運勢': value,
                    '回数': count,
                    '割合(%)': f"{percentage:.1f}"
                })
        
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(output_dir, f'{gender}_results.csv'), index=False, encoding='utf-8-sig')

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

    # 結果を出力
    output_dir = 'analysis_results'
    create_graphs(results, output_dir)
    create_html_report(results, output_dir)
    export_to_csv(results, output_dir)
    
    logger.info(f"分析結果を {output_dir} ディレクトリに保存しました")

if __name__ == '__main__':
    analyze_fortune_patterns() 