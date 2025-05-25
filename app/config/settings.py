"""アプリケーション設定モジュール"""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定クラス"""

    # Flask設定
    flask_app: str = Field(default="app.main", alias="FLASK_APP")
    flask_env: str = Field(default="development", alias="FLASK_ENV")
    flask_debug: bool = Field(default=True, alias="FLASK_DEBUG")
    secret_key: str = Field(default="dev-key", alias="SECRET_KEY")

    # データベース設定
    database_path: str = Field(default="names.db", alias="DATABASE_PATH")

    # ログ設定
    log_level: str = Field(default="DEBUG", alias="LOG_LEVEL")

    # アプリケーション設定
    timeout: int = Field(default=3600, alias="TIMEOUT")
    max_concurrent_requests: int = Field(default=4, alias="MAX_CONCURRENT_REQUESTS")

    # スクレイピング設定
    scraping_delay: float = Field(default=0.5, alias="SCRAPING_DELAY")
    request_timeout: int = Field(default=30, alias="REQUEST_TIMEOUT")

    # セキュリティ設定
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"], alias="ALLOWED_HOSTS"
    )
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5000"],
        alias="CORS_ORIGINS",
    )

    # 外部API設定
    enamae_base_url: str = Field(
        default="https://enamae.net", alias="ENAMAE_BASE_URL"
    )
    namaeuranai_base_url: str = Field(
        default="https://namaeuranai.biz", alias="NAMAEURANAI_BASE_URL"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


# シングルトンインスタンス
settings = Settings()
