"""ローカルSQLiteデータベース層。

ダッシュボード(Home.py / pages/*.py)は、この層を経由してのみデータを読む。
FREDへの実際のアクセスは、管理者ページ(pages/0_管理者ページ.py)からの
`refresh_all()` 呼び出し時にのみ発生する。

テーブル構成:
  observations   : series_id ごとの時系列データ本体 (series_id, date) が主キー
  series_status  : series_id ごとの最終更新日時・最終エラーを記録
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import SERIES
from src.data_fetcher import DataFetchError, fetch_from_fred

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = _PROJECT_ROOT / "data" / "macro_dashboard.sqlite3"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    series_id TEXT NOT NULL,
    date TEXT NOT NULL,
    value REAL NOT NULL,
    PRIMARY KEY (series_id, date)
);

CREATE TABLE IF NOT EXISTS series_status (
    series_id TEXT PRIMARY KEY,
    last_updated_at TEXT,
    last_error TEXT
);
"""


@contextmanager
def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(_SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def all_series_ids() -> list[str]:
    """config.SERIES に登録されている全FRED系列IDを返す。"""
    ids: list[str] = []
    for metric in SERIES.values():
        for info in metric["countries"].values():
            ids.append(info["id"])
    return ids


def load_series(series_id: str) -> pd.Series:
    """DBから時系列データ(pandas.Series, index=日付)を読み出す。未取得なら空のSeries。"""
    with _connect() as conn:
        df = pd.read_sql_query(
            "SELECT date, value FROM observations WHERE series_id = ? ORDER BY date",
            conn,
            params=(series_id,),
            parse_dates=["date"],
        )
    return pd.Series(df["value"].values, index=df["date"], name=series_id)


def load_latest(series_id: str) -> tuple[pd.Timestamp | None, float | None]:
    """DBに保存されている最新の日付・値を返す。データが無ければ (None, None)。"""
    series = load_series(series_id)
    if series.empty:
        return None, None
    return series.index[-1], float(series.iloc[-1])


def get_status(series_id: str) -> dict:
    """series_status テーブルから最終更新日時・最終エラーを返す。未更新なら両方None。"""
    with _connect() as conn:
        row = conn.execute(
            "SELECT last_updated_at, last_error FROM series_status WHERE series_id = ?",
            (series_id,),
        ).fetchone()
    if row is None:
        return {"last_updated_at": None, "last_error": None}
    return {"last_updated_at": row[0], "last_error": row[1]}


def _save_series(conn: sqlite3.Connection, series_id: str, series: pd.Series) -> None:
    conn.execute("DELETE FROM observations WHERE series_id = ?", (series_id,))
    rows = [(series_id, idx.strftime("%Y-%m-%d"), float(val)) for idx, val in series.items()]
    conn.executemany(
        "INSERT INTO observations (series_id, date, value) VALUES (?, ?, ?)", rows
    )


def _mark_status(conn: sqlite3.Connection, series_id: str, error: str | None) -> None:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    conn.execute(
        """
        INSERT INTO series_status (series_id, last_updated_at, last_error)
        VALUES (?, ?, ?)
        ON CONFLICT(series_id) DO UPDATE SET last_updated_at = excluded.last_updated_at,
                                              last_error = excluded.last_error
        """,
        (series_id, now, error),
    )


def refresh_series(series_id: str) -> tuple[bool, str | None]:
    """FREDから1系列を取得してDBに保存する。成功可否と、失敗時のエラーメッセージを返す。"""
    with _connect() as conn:
        try:
            series = fetch_from_fred(series_id)
            _save_series(conn, series_id, series)
            _mark_status(conn, series_id, error=None)
            return True, None
        except DataFetchError as e:
            _mark_status(conn, series_id, error=str(e))
            return False, str(e)


def refresh_all() -> dict[str, tuple[bool, str | None]]:
    """config.SERIES に登録された全系列をFREDから取得し、DBへ保存する。

    管理者ページの「DB更新」ボタンから呼ばれる。
    戻り値は {series_id: (成功可否, エラーメッセージ)} の辞書。
    """
    results: dict[str, tuple[bool, str | None]] = {}
    for series_id in all_series_ids():
        results[series_id] = refresh_series(series_id)
    return results
