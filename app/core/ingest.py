import os
import sqlite3
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

# 名前データベースのパス
DB_PATH = os.getenv('NAME_DB_PATH', 'names.db')


def ingest_pattern(
    chars: int,
    strokes1: int,
    strokes2: Optional[int] = None,
    strokes3: Optional[int] = None,
    gender: str = 'male'
) -> None:
    """
    指定されたパターン（画数・文字数・性別）に該当する名前を
    「赤ちゃん命名ガイド」からスクレイピングしてデータベースに保存する。

    :param chars: 文字数（1,2,3）
    :param strokes1: 1文字目の画数
    :param strokes2: 2文字目の画数（chars>=2）
    :param strokes3: 3文字目の画数（chars==3）
    :param gender: 'male' or 'female'
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # URLパス生成
    sex_path = 'm' if gender == 'male' else 'f'
    strokes_list = [strokes1] + ([strokes2] if chars >= 2 else []) + ([strokes3] if chars == 3 else [])
    strokes_param = ','.join(str(s) for s in strokes_list)
    base_url = f'https://b-name.jp/赤ちゃん名前辞典/{sex_path}/jikaku/{strokes_param}/'

    # 初期文字選択ページを取得し、div.malenamelist_boxから文字リンクを抽出
    print(f"[Debug] base_url: {base_url}")
    # セキュリティ強化：タイムアウト設定
    resp = requests.get(base_url, timeout=30)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # テーブル形式の名前リストがあれば優先して取得
    rows = soup.select('div.namelist.jikakuListBox table tbody tr')
    print(f"[Debug] table rows: {len(rows)}")
    if rows:
        for row in rows:
            name_tag = row.select_one('td.cell-name span')
            yomi_tag = row.select_one('td.cell-yomi span')
            detail_link = row.select_one('td.cell-name a')
            if detail_link:
                detail_href = detail_link.get('href')
                name = name_tag.get_text(strip=True) if name_tag else ''
                yomi = yomi_tag.get_text(strip=True) if yomi_tag else ''
                source_url = 'https://b-name.jp' + detail_href
                total = sum(s for s in strokes_list if s is not None)
                try:
                    cur.execute(
                        "INSERT OR IGNORE INTO names(name, yomi, chars, strokes_1, strokes_2, strokes_3, total_strokes, gender, source_url) VALUES(?,?,?,?,?,?,?,?,?)",
                        (name, yomi, chars,
                         strokes_list[0],
                         strokes_list[1] if chars >= 2 else None,
                         strokes_list[2] if chars == 3 else None,
                         total, gender, source_url)
                    )
                    conn.commit()
                except Exception:
                    conn.rollback()
                time.sleep(0.5)
        conn.close()
        return
    # fallback: 文字別リンク方式（男性／その他ケース）
    letter_links = [a['href'] for a in soup.select('div.malenamelist_box ul:nth-of-type(2) li a')]
    print(f"[Debug] fallback letter_links: {letter_links}")
    # 各文字ごとの名前リストを取得
    for link in letter_links:
        page_url = 'https://b-name.jp' + link
        print(f"[Debug] fetching letter page: {page_url}")
        # セキュリティ強化：タイムアウト設定
        r2 = requests.get(page_url, timeout=30)
        s2 = BeautifulSoup(r2.text, 'html.parser')
        name_links = s2.select('div.malenamelist_box ul.ml-box li a')
        print(f"[Debug] found {len(name_links)} name links on {page_url}")
        print(f"[Debug] sample names: {[a.get_text(strip=True) for a in name_links[:5]]}")
        for a in name_links:
            name = a.get_text(strip=True)
            detail_path = a.get('href')
            if detail_path:
                detail_url = 'https://b-name.jp' + detail_path
                # 詳細ページで読みを取得
                # セキュリティ強化：タイムアウト設定
                r3 = requests.get(detail_url, timeout=30)
                s3 = BeautifulSoup(r3.text, 'html.parser')
                yomi_tag = s3.select_one('span.yomi')
                yomi = yomi_tag.get_text(strip=True) if yomi_tag else ''
                total = sum(s for s in strokes_list if s is not None)
                # DB保存
                try:
                    cur.execute(
                        "INSERT OR IGNORE INTO names(name, yomi, chars, strokes_1, strokes_2, strokes_3, total_strokes, gender, source_url) VALUES(?,?,?,?,?,?,?,?,?)",
                        (name, yomi, chars, strokes_list[0], strokes_list[1] if chars>=2 else None,
                         strokes_list[2] if chars==3 else None, total, gender, detail_url)
                    )
                    conn.commit()
                except Exception:
                    conn.rollback()
                # サーバー負荷軽減
                time.sleep(0.5)
    conn.close() 