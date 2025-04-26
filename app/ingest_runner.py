#!/usr/bin/env python3
"""
CLI スクリプト: 赤ちゃん命名ガイドから名前候補データを SQLite DB に投入する
"""
import argparse
import sys
from app.core.ingest import ingest_pattern


def main():
    parser = argparse.ArgumentParser(
        description='赤ちゃん命名ガイドから名前データをSQLite DBに投入するCLI'
    )
    parser.add_argument('--chars', type=int, required=True, choices=[1, 2, 3], help='名前の文字数 (1, 2, 3)')
    parser.add_argument('--strokes1', type=int, required=True, help='1文字目の画数')
    parser.add_argument('--strokes2', type=int, help='2文字目の画数 (文字数2以上の場合必須)')
    parser.add_argument('--strokes3', type=int, help='3文字目の画数 (文字数3の場合必須)')
    parser.add_argument('--gender', type=str, default='male', choices=['male', 'female'], help='性別 (male or female)')

    args = parser.parse_args()

    # バリデーション
    if args.chars >= 2 and args.strokes2 is None:
        print('Error: --strokes2 は文字数2以上の場合必須です', file=sys.stderr)
        sys.exit(1)
    if args.chars == 3 and args.strokes3 is None:
        print('Error: --strokes3 は文字数3の場合必須です', file=sys.stderr)
        sys.exit(1)

    print(f"[INGEST] chars={args.chars}, strokes1={args.strokes1}, strokes2={args.strokes2}, strokes3={args.strokes3}, gender={args.gender}")
    try:
        ingest_pattern(
            chars=args.chars,
            strokes1=args.strokes1,
            strokes2=args.strokes2,
            strokes3=args.strokes3,
            gender=args.gender
        )
        print('[INGEST] Completed successfully.')
    except Exception as e:
        print(f'[INGEST] Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main() 