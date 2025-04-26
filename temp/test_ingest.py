#!/usr/bin/env python3
"""
テストスクリプト: app/core/ingest.ingest_pattern の動作確認用
Usage:
  $ python temp/test_ingest.py
"""
import os
import sys
import sqlite3
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# プロジェクトルートをPythonパスに追加
script_dir = Path(__file__).parent.resolve()
project_root = script_dir.parent.resolve()
sys.path.insert(0, str(project_root))

# テスト用ディレクトリとDBパスの設定
db_path = script_dir / 'test_names.db'
os.environ['NAME_DB_PATH'] = str(db_path)

# DBファイルがあれば削除
if db_path.exists():
    db_path.unlink()
print(f"[Setup] Test DB Path: {db_path}")

# テスト対象関数をインポート
from app.core.ingest import ingest_pattern
from app.core.name_generator import init_db

# テストパラメータ
chars = 1
strokes1 = 2
strokes2 = None
strokes3 = None
gender = 'male'

# DB テーブル初期化
init_db()

# -- デバッグ用: ページ取得とセレクタテスト --
print("[Debug] Fetching page for inspection...")
# ingest_patternと同じURL構築
sex_path = 'm' if gender == 'male' else 'f'
strokes_list = [strokes1] + ([strokes2] if chars >= 2 and strokes2 is not None else []) + ([strokes3] if chars == 3 and strokes3 is not None else [])
strokes_param = ','.join(str(s) for s in strokes_list)
base_url = f'https://b-name.jp/赤ちゃん名前辞典/{sex_path}/jikaku/{strokes_param}/'
resp = requests.get(base_url)
print(f"[Debug] Requested URL: {resp.url}")
print(f"[Debug] Status Code: {resp.status_code}")
html_snippet = resp.text[:1000].replace('\n',' ')
print(f"[Debug] HTML snippet (first 500 chars): {html_snippet[:500]}")
soup = BeautifulSoup(resp.text, 'html.parser')
# デバッグ: ulタグのクラス一覧とliタグ数を表示
uls = soup.find_all('ul')
print(f"[Debug] 総ULタグ数: {len(uls)}")
for ul in uls[:10]:  # 最初の10件のみ表示
    print(f"[Debug] UL class: {ul.get('class')}")
lis = soup.find_all('li')
print(f"[Debug] 総LIタグ数: {len(lis)}")
# 最初の5つのLIタグ内容を表示
for i, li in enumerate(lis[:5], start=1):
    print(f"[Debug] LI[{i}]: {li}")
sel_old = soup.select('.babyname_list li')
sel_new = soup.select('.babyname-list li')
print(f"[Debug] .babyname_list li count: {len(sel_old)}")
print(f"[Debug] .babyname-list li count: {len(sel_new)}")
# 全クラス名一覧を収集
unique_classes = set()
for tag in soup.find_all(class_=True):
    classes = tag.get('class') or []
    for cl in classes:
        unique_classes.add(cl)
print(f"[Debug] Unique classes on page ({len(unique_classes)}): {sorted(unique_classes)}")

# `div.malenamelist_box` の要素とリスト内容を出力
divs_mb = soup.select('.malenamelist_box')
print(f"[Debug] '.malenamelist_box' elements count: {len(divs_mb)}")
if divs_mb:
    first_mb = divs_mb[0]
    uls_mb = first_mb.find_all('ul')
    print(f"[Debug] '.malenamelist_box' 内のULタグ数: {len(uls_mb)}")
    for i, ul in enumerate(uls_mb[:2], start=1):
        lis_mb = ul.find_all('li')
        print(f"[Debug] UL[{i}] class: {ul.get('class')}, LI count: {len(lis_mb)}")
        for j, li in enumerate(lis_mb[:3], start=1):
            print(f"[Debug] UL[{i}] LI[{j}]: {li.get_text(strip=True)}")

print(f"[Test] ingest_pattern(chars={chars}, strokes1={strokes1}, gender={gender}) を実行中... ")
try:
    ingest_pattern(chars=chars, strokes1=strokes1, strokes2=strokes2, strokes3=strokes3, gender=gender)
    print("[Done] スクレイピング＆DB挿入完了")
except Exception as e:
    print(f"[Error] ingest_pattern 実行中に例外発生: {e}")
    sys.exit(1)

# DB接続してデータ件数を取得
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()
try:
    cur.execute('SELECT COUNT(*) FROM names')
    count = cur.fetchone()[0]
    print(f"[Result] テーブル 'names' の件数: {count}")
    # サンプルデータを表示
    cur.execute('SELECT name, yomi, total_strokes, source_url FROM names LIMIT 5')
    rows = cur.fetchall()
    print("[Sample Rows]")
    for row in rows:
        print(row)
finally:
    conn.close() 