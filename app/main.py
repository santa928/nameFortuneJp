# 標準ライブラリ
import json
import logging
import os
from typing import Any

# サードパーティライブラリ
from flask import Flask, jsonify, render_template, request
from pydantic import ValidationError
from werkzeug.serving import WSGIRequestHandler

# ロギング設定を中央集権化
from app.core.logging_config import setup_logging
from app.core.models import ErrorResponse, FortuneRequest

# ローカルアプリケーション
from app.core.scraper import create_scraper
from app.core.stroke_analysis import AnalysisProgressStore, StrokeAnalysisService

# タイムアウトを60分に設定
WSGIRequestHandler.protocol_version = "HTTP/1.1"
os.environ["PYTHONUNBUFFERED"] = "1"

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.logger.setLevel(logging.DEBUG)
app.config["TIMEOUT"] = 3600
scraper = create_scraper()
progress_store = AnalysisProgressStore()
stroke_analysis_service = StrokeAnalysisService(progress_store)


# 先にロギングを初期化
setup_logging()


def load_fortune_types() -> Any:
    """運勢タイプのJSONファイルを読み込む"""
    with open("app/config/fortune_types.json", "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index() -> Any:
    """通常の姓名判断ページを表示"""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze() -> Any:
    """姓名判断API - Pydanticモデルを使用した型安全な実装"""
    try:
        # Pydanticモデルによる自動バリデーション
        request_data = FortuneRequest(**request.get_json())

        app.logger.debug(
            f"リクエスト: 姓={request_data.last_name}, "
            f"名={request_data.first_name}, 性別={request_data.gender}"
        )

        # バリデーション済みのデータを使用
        raw_results = scraper.get_fortune(
            request_data.last_name,
            request_data.first_name,
            request_data.gender,
        )
        app.logger.debug(f"スクレイピング結果: {raw_results}")

        if "error" in raw_results:
            app.logger.error(f"スクレイピングエラー: {raw_results['error']}")
            error_response = ErrorResponse(error=str(raw_results["error"]))
            return jsonify(error_response.model_dump()), 500

        # UIが期待する形式に変換
        results = {
            "enamae": raw_results.get("enamae.net", {}),
            "namaeuranai": raw_results.get("namaeuranai.biz", {}),
        }

        app.logger.debug(f"変換後の結果: {results}")
        return jsonify(results)

    except ValidationError as e:
        # Pydanticバリデーションエラー
        app.logger.warning(f"バリデーションエラー: {e}")
        error_response = ErrorResponse(error=f"入力データが不正です: {str(e)}")
        return jsonify(error_response.model_dump()), 400

    except Exception as e:
        app.logger.exception("予期せぬエラーが発生しました")
        error_response = ErrorResponse(error=f"サーバーエラー: {str(e)}")
        return jsonify(error_response.model_dump()), 500


@app.route("/analyze_progress/<queue_id>")
def get_progress(queue_id: str) -> Any:
    """進捗状況を返すエンドポイント"""
    progress = progress_store.get(queue_id)
    return jsonify(progress)


@app.route("/analyze_strokes", methods=["GET", "POST"])
async def analyze_strokes() -> Any:
    """画数パターン分析ページ"""
    if request.method == "POST":
        try:
            data = request.get_json()
            last_name = data.get("last_name")
            char_count = int(data.get("char_count", 1))

            # バリデーション
            if not last_name:
                return jsonify({"error": "名字を入力してください"}), 400
            if not 1 <= char_count <= 3:
                return jsonify({"error": "文字数は1から3の間で指定してください"}), 400

            queue_id = stroke_analysis_service.start_analysis(last_name, char_count)

            return jsonify({"success": True, "queue_id": queue_id}), 202  # Accepted

        except Exception as e:
            app.logger.exception("画数パターン分析中にエラーが発生しました")
            return jsonify({"error": str(e)}), 500

    return render_template("analyze_strokes.html")


@app.route("/healthz")
def healthz() -> Any:
    """コンテナ・ロードバランサ用ヘルスチェック"""
    return "ok", 200


if __name__ == "__main__":
    # 環境変数でデバッグモードを制御（本番環境ではFalse）
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    host = os.getenv("FLASK_HOST", "0.0.0.0")  # nosec B104
    port = int(os.getenv("FLASK_PORT", "5000"))

    app.config["TIMEOUT"] = 3600
    app.run(
        debug=debug_mode,
        host=host,
        port=port,
        threaded=True,
        request_handler=WSGIRequestHandler,
    )
