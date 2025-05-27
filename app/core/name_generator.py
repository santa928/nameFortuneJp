import os
import sqlite3
from typing import Dict, List, Optional

# データベースファイルのパス（環境変数NAME_DB_PATHで設定可能）
DB_PATH = os.getenv("NAME_DB_PATH", "names.db")


def init_db() -> None:
    """
    SQLiteデータベースと names テーブルを初期化する。
    初回起動時またはスキーマ更新時に実行してください。
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            yomi TEXT,
            chars INTEGER NOT NULL,
            strokes_1 INTEGER NOT NULL,
            strokes_2 INTEGER,
            strokes_3 INTEGER,
            total_strokes INTEGER NOT NULL,
            gender TEXT NOT NULL,
            source_url TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


def get_name_candidates(
    chars: int,
    strokes1: int,
    strokes2: Optional[int] = None,
    strokes3: Optional[int] = None,
    gender: Optional[str] = None,
) -> List[Dict[str, str]]:
    """
    指定された文字数、各文字の画数、性別に合致する名前候補を最大50件取得する。

    :param chars: 名前の文字数（1,2,3）
    :param strokes1: 1文字目の画数
    :param strokes2: 2文字目の画数（chars>=2の場合必須）
    :param strokes3: 3文字目の画数（chars==3の場合必須）
    :param gender: 性別フィルタ ('male','female','unisex')
    :return: 候補リスト（dict: {name, yomi, gender}）
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ベースクエリ
    query = (
        "SELECT name, yomi, gender FROM names "
        "WHERE chars = ? AND strokes_1 = ?"
    )
    params: List = [chars, strokes1]

    # 2文字目・3文字目の画数条件
    if chars >= 2:
        query += " AND strokes_2 = ?"
        params.append(strokes2)
    if chars == 3:
        query += " AND strokes_3 = ?"
        params.append(strokes3)

    # 性別条件
    if gender:
        query += " AND gender = ?"
        params.append(gender)

    # 最大50件
    query += " LIMIT 50"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    # 結果を辞書化
    candidates: List[Dict[str, str]] = []
    for name, yomi, g in rows:
        candidates.append({"name": name, "yomi": yomi or "", "gender": g})
    return candidates
