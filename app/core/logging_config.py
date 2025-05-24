import logging
import os
from typing import Optional


def setup_logging(level: Optional[int] = None) -> None:
    """アプリ全体のロギング設定を初期化するユーティリティ

    Args:
        level (Optional[int]): ログレベル。未指定なら環境変数 LOG_LEVEL か INFO。
    """
    if level is None:
        env_level = os.getenv("LOG_LEVEL")
        level = getattr(logging, env_level.upper(), logging.INFO) if env_level else logging.INFO

    # basicConfig は 1 回だけ有効になるため、何度呼ばれても問題ない
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    ) 