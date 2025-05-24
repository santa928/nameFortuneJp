"""アプリケーション設定モジュール"""
import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定クラス"""
    
    # Flask設定
    flask_app: str = Field(default="app.main", env="FLASK_APP")
    flask_env: str = Field(default="development", env="FLASK_ENV")
    flask_debug: bool = Field(default=True, env="FLASK_DEBUG")
    secret_key: str = Field(default="dev-key", env="SECRET_KEY")
    
    # データベース設定
    database_path: str = Field(default="names.db", env="DATABASE_PATH")
    
    # ログ設定
    log_level: str = Field(default="DEBUG", env="LOG_LEVEL")
    
    # アプリケーション設定
    timeout: int = Field(default=3600, env="TIMEOUT")
    max_concurrent_requests: int = Field(default=4, env="MAX_CONCURRENT_REQUESTS")
    
    # スクレイピング設定
    scraping_delay: float = Field(default=0.5, env="SCRAPING_DELAY")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    
    # セキュリティ設定
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"], 
        env="ALLOWED_HOSTS"
    )
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5000"],
        env="CORS_ORIGINS"
    )
    
    # 外部API設定
    enamae_base_url: str = Field(default="https://enamae.net", env="ENAMAE_BASE_URL")
    namaeuranai_base_url: str = Field(default="https://namaeuranai.biz", env="NAMAEURANAI_BASE_URL")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


# シングルトンインスタンス
settings = Settings() 