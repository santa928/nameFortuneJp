from flask import Flask, render_template, request, jsonify, session, Response
import logging
from scraper import create_scraper
import json
from typing import Dict, List
from fortune_analyzer import FortuneAnalyzer, get_character_by_strokes
import asyncio
import os
import queue
import threading

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.logger.setLevel(logging.DEBUG)
scraper = create_scraper()

# プログレス情報を保持するグローバル変数
progress_queues = {}

def load_fortune_types() -> Dict[str, List[str]]:
    """運勢タイプのJSONファイルを読み込む"""
    with open('fortune_types.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    """通常の姓名判断ページを表示"""
    return render_template('index.html')

@app.route('/stroke_list', methods=['GET', 'POST'])
def stroke_list():
    """画数別運勢一覧ページを表示"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            last_name = data.get('last_name', '')
            
            if not last_name:
                return jsonify({'error': '姓を入力してください'}), 400
            
            # 1画から20画までの結果を取得
            results = {}
            for strokes in range(1, 21):
                # 画数に対応する文字を使用
                test_name = get_character_by_strokes(strokes)
                fortune_result = scraper.get_fortune(last_name, test_name, 'm', stroke_list_mode=True)  # 男性固定
                
                if 'error' not in fortune_result:
                    results[str(strokes)] = {
                        'test_name': test_name,
                        'fortune': fortune_result
                    }
            
            # 結果を直接返す
            return jsonify({
                'success': True,
                'results': results,
                'last_name': last_name
            })
        
        except Exception as e:
            app.logger.exception("予期せぬエラーが発生しました")
            return jsonify({'error': str(e)}), 500
    
    # GETリクエストの場合は、セッションから結果を取得して表示
    try:
        results = session.get('stroke_results', {})
        last_name = session.get('last_name', '')
        return render_template('stroke_list.html', results=results, last_name=last_name)
    except Exception as e:
        app.logger.exception("予期せぬエラーが発生しました")
        return render_template('stroke_list.html', error=str(e))

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

def get_character_by_strokes(strokes):
    # 画数に対応する文字を返す
    stroke_characters = {
        1: '一', 2: '二', 3: '三', 4: '中', 5: '兄',
        6: '両', 7: '乱', 8: '並', 9: '乗', 10: '俺',
        11: '停', 12: '博', 13: '働', 14: '僕', 15: '劇',
        16: '疑', 17: '優', 18: '儲', 19: '爆', 20: '競'
    }
    return stroke_characters.get(strokes, '一')

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

@app.route('/analyze_progress')
def progress():
    """分析の進捗状況を提供するServer-Sent Eventsエンドポイント"""
    def generate():
        queue_id = request.args.get('queue_id', 'default')
        q = progress_queues.get(queue_id, queue.Queue())
        
        while True:
            try:
                progress = q.get(timeout=1.0)
                yield f"data: {json.dumps({'progress': progress})}\n\n"
                if progress >= 100:
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'progress': 0})}\n\n"
            
    return Response(generate(), mimetype='text/event-stream')

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
            
            # 進捗情報用のキューを作成
            queue_id = f"{last_name}_{char_count}"
            progress_queues[queue_id] = queue.Queue()
            
            # 分析実行（性別は男性固定）
            analyzer = FortuneAnalyzer()
            
            # 進捗コールバック関数
            async def progress_callback(progress_rate: float, pattern: List[int]):
                progress_queues[queue_id].put(progress_rate)
                app.logger.debug(f"Progress: {progress_rate}%, Pattern: {pattern}")
            
            # 分析実行
            results = await analyzer.analyze(last_name=last_name, char_count=char_count, progress_callback=progress_callback)
            
            # 結果をJSONファイルに保存
            filename = f'static/results_{last_name}_{char_count}字.json'
            os.makedirs('static', exist_ok=True)
            await analyzer.save_results(results, filename)
            
            # 進捗情報用のキューを削除
            del progress_queues[queue_id]
            
            return jsonify({
                'success': True,
                'results': results,
                'filename': filename,
                'queue_id': queue_id
            })
            
        except Exception as e:
            app.logger.exception("画数パターン分析中にエラーが発生しました")
            return jsonify({'error': str(e)}), 500
    
    return render_template('analyze_strokes.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 