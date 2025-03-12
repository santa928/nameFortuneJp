from flask import Flask, render_template, request, jsonify
import logging
from scraper import create_scraper

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
scraper = create_scraper()

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 