"""構造化ログ設定モジュール"""
import sys
import structlog
from typing import Any, Dict


def setup_logging() -> None:
    """構造化ログの設定を行う"""
    
    # 標準ライブラリのloggingとstructlogを統合
    structlog.configure(
        processors=[
            # 構造化ログ用のプロセッサー
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # JSON形式で出力（本番環境向け）
            structlog.processors.JSONRenderer() if _is_production() else structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def _is_production() -> bool:
    """本番環境かどうかを判定"""
    import os
    return os.getenv("FLASK_ENV", "development") == "production"


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """構造化ログインスタンスを取得"""
    return structlog.get_logger(name)


# アプリケーション用のログファクトリ
def create_app_logger(context: Dict[str, Any] = None) -> structlog.stdlib.BoundLogger:
    """アプリケーション用のログインスタンスを作成"""
    logger = get_logger("namefortune")
    if context:
        logger = logger.bind(**context)
    return logger 