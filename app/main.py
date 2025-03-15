# 標準ライブラリ
import asyncio
import json
import logging
import os
import threading
from typing import Dict, List

# サードパーティライブラリ
from flask import Flask, render_template, request, jsonify
from werkzeug.serving import WSGIRequestHandler

# ローカルアプリケーション
from app.core.scraper import create_scraper
from app.core.fortune_analyzer import FortuneAnalyzer, get_character_by_strokes
from app.core.request_context import copy_current_request_context

# タイムアウトを60分に設定
WSGIRequestHandler.protocol_version = "HTTP/1.1"
os.environ['PYTHONUNBUFFERED'] = '1'

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.logger.setLevel(logging.DEBUG)
app.config['TIMEOUT'] = 3600
scraper = create_scraper()

# プログレス情報を保持するグローバル変数
analysis_progress = {}

def load_fortune_types() -> Dict[str, List[str]]:
    """運勢タイプのJSONファイルを読み込む"""
    with open('app/config/fortune_types.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    """通常の姓名判断ページを表示"""
    return render_template('index.html')

@app.route('/name_generator')
def name_generator():
    return render_template('name_generator.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        last_name = data.get('last_name', '')
        gender = data.get('gender', 'm')
        
        app.logger.debug(f"リクエスト: 姓={last_name}, 性別={gender}")
        
        if not last_name:
            return jsonify({'error': '名字を入力してください'}), 400
        
        # 1画から20画までの結果を取得
        results = {}
        for strokes in range(1, 21):
            # 仮の名として画数に対応する文字を使用
            test_name = get_character_by_strokes(strokes)
            fortune_result = scraper.get_fortune(last_name, test_name, gender)
            
            if 'error' not in fortune_result:
                results[str(strokes)] = fortune_result
        
        return jsonify({
            'last_name': last_name,
            'results': results
        })
    
    except Exception as e:
        app.logger.exception("予期せぬエラーが発生しました")
        return jsonify({'error': f"サーバーエラー: {str(e)}"}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        last_name = data.get('last_name', '')
        first_name = data.get('first_name', '')
        gender = data.get('gender', 'm')
        
        app.logger.debug(f"リクエスト: 姓={last_name}, 名={first_name}, 性別={gender}")
        
        if not last_name or not first_name:
            return jsonify({'error': '姓名を入力してください'}), 400
        
        results = scraper.get_fortune(last_name, first_name, gender)
        app.logger.debug(f"スクレイピング結果: {results}")
        
        if 'error' in results:
            app.logger.error(f"スクレイピングエラー: {results['error']}")
            return jsonify({'error': results['error']}), 500
        
        return jsonify(results)
    
    except Exception as e:
        app.logger.exception("予期せぬエラーが発生しました")
        return jsonify({'error': f"サーバーエラー: {str(e)}"}), 500

@app.route('/analyze_progress/<queue_id>')
def get_progress(queue_id):
    """進捗状況を返すエンドポイント"""
    progress = analysis_progress.get(queue_id, {})
    return jsonify(progress)

@app.route('/analyze_strokes', methods=['GET', 'POST'])
async def analyze_strokes():
    """画数パターン分析ページ"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            last_name = data.get('last_name')
            char_count = int(data.get('char_count', 1))
            
            # バリデーション
            if not last_name:
                return jsonify({'error': '名字を入力してください'}), 400
            if not 1 <= char_count <= 3:
                return jsonify({'error': '文字数は1から3の間で指定してください'}), 400
            
            # 進捗情報用のIDを作成
            queue_id = f"{last_name}_{char_count}"
            
            # 進捗状況を初期化
            analysis_progress[queue_id] = {
                'progress': 0,
                'status': 'running'
            }
            
            # バックグラウンドタスクとして分析を実行
            def run_analysis():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    async def analyze():
                        try:
                            # 分析実行（性別は男性固定）
                            analyzer = FortuneAnalyzer()
                            
                            # 進捗コールバック関数
                            async def progress_callback(progress_rate: float, pattern: List[int]):
                                analysis_progress[queue_id] = {
                                    'progress': progress_rate,
                                    'status': 'running',
                                    'pattern': pattern
                                }
                                app.logger.debug(f"Progress for {queue_id}: {progress_rate}%, Pattern: {pattern}")
                            
                            # 分析実行
                            results = await analyzer.analyze(last_name=last_name, char_count=char_count, progress_callback=progress_callback)
                            
                            # 結果をJSONファイルに保存
                            filename = f'static/results_{last_name}_{char_count}字.json'
                            os.makedirs('static', exist_ok=True)
                            await analyzer.save_results(results, filename)
                            
                            # 完了を通知
                            analysis_progress[queue_id] = {
                                'progress': 100,
                                'status': 'complete',
                                'results': results
                            }
                                
                        except Exception as e:
                            app.logger.exception("分析処理中にエラーが発生しました")
                            analysis_progress[queue_id] = {
                                'progress': -1,
                                'status': 'error',
                                'error': str(e)
                            }
                    
                    loop.run_until_complete(analyze())
                    loop.close()
                    
                except Exception as e:
                    app.logger.exception("分析スレッドでエラーが発生しました")
                    analysis_progress[queue_id] = {
                        'progress': -1,
                        'status': 'error',
                        'error': str(e)
                    }
            
            thread = threading.Thread(target=run_analysis)
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'queue_id': queue_id
            }), 202  # Accepted
            
        except Exception as e:
            app.logger.exception("画数パターン分析中にエラーが発生しました")
            return jsonify({'error': str(e)}), 500
    
    return render_template('analyze_strokes.html')

if __name__ == '__main__':
    # デバッグモードを有効にし、タイムアウトを60分に設定
    app.config['TIMEOUT'] = 3600
    app.run(debug=True, host='0.0.0.0', threaded=True, request_handler=WSGIRequestHandler) 