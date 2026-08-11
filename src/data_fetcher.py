"""FRED (Federal Reserve Economic Data) への実際のアクセスを担うモジュール。

このモジュールを直接呼ぶのは `src/db.py` の `refresh_series()` / `refresh_all()` のみ。
ダッシュボード画面(Home.py / pages/*.py)は `src/db.py` 経由でローカルDBを読むだけで、
FREDへは一切アクセスしない(FREDへのアクセスは管理者ページの更新ボタンからのみ発生する)。
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# プロジェクトルートの .env を読み込む(.envが無くても環境変数があればそれを使う)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

FRED_API_KEY_HELP = (
    "FRED_API_KEY が設定されていません。\n\n"
    "1. https://fred.stlouisfed.org/docs/api/api_key.html で無料のAPIキーを取得してください。\n"
    "2. プロジェクト直下に `.env` ファイルを作成し、次の1行を追加してください。\n"
    "   `FRED_API_KEY=取得したキー`\n"
    "3. アプリを再起動してください。"
)


class DataFetchError(Exception):
    """データ取得に失敗したときに送出する例外。メッセージはそのままUIに表示できる文言にする。"""


def _get_fred_client():
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise DataFetchError(FRED_API_KEY_HELP)

    # fredapi は必須依存だが遅延importにして、キー未設定時は
    # importエラーではなく上のわかりやすいメッセージを優先させる。
    from fredapi import Fred

    return Fred(api_key=api_key)


def fetch_from_fred(series_id: str) -> pd.Series:
    """指定したFRED系列IDの時系列データ(pandas.Series, index=日付)をFREDから直接取得する。"""
    try:
        fred = _get_fred_client()
        series = fred.get_series(series_id).dropna()
        series.index.name = "date"
        return series
    except DataFetchError:
        raise
    except Exception as exc:  # noqa: BLE001 - APIエラーの種類を問わずメッセージ化したい
        raise DataFetchError(
            f"FREDからのデータ取得に失敗しました(系列ID: {series_id})。\n{exc}"
        ) from exc
