"""マクロ経済ダッシュボードの最新データからMarkdownレポートを生成する。

実行方法(プロジェクトルートから、またはどこからでも可):
    python .claude/skills/macro-dashboard/scripts/generate_report.py

- src/config.py の SERIES 定義と src/data_fetcher.fetch_series() を使って全指標を取得する。
  data_cache/ に既存キャッシュがあればそれを使うため、FRED_API_KEY が未設定でも
  一度でも取得済みの環境なら動く(未取得の系列は「取得失敗」としてレポートに記載する)。
- 各指標について、最新値・前回値からの変化・1年前からの変化(概算)をまとめる。
- 出力は reports/YYYYMMDD_macro_report.md に保存する。
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd

# scripts/ -> macro-dashboard/ -> skills/ -> .claude/ -> プロジェクトルート
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import SERIES  # noqa: E402
from src.data_fetcher import DataFetchError, fetch_series  # noqa: E402


def _change_desc(series: pd.Series) -> str:
    """直近2点間の変化を短い文言にする。"""
    if len(series) < 2:
        return "変化なし(データ不足)"
    diff = series.iloc[-1] - series.iloc[-2]
    if diff > 0:
        return f"🔺 前回比 {diff:+.2f}"
    if diff < 0:
        return f"🔻 前回比 {diff:+.2f}"
    return "→ 前回比 横ばい"


def _yoy_desc(series: pd.Series) -> str | None:
    """1年前の直近値と比較した変化を短い文言にする。データが無ければNone。"""
    if series.empty:
        return None
    target = series.index[-1] - pd.DateOffset(years=1)
    prior = series[series.index <= target]
    if prior.empty:
        return None
    diff = series.iloc[-1] - prior.iloc[-1]
    base = prior.iloc[-1]
    if base:
        return f"前年同期比 {diff:+.2f} ({diff / base * 100:+.1f}%)"
    return f"前年同期比 {diff:+.2f}"


def build_report() -> str:
    lines: list[str] = [
        f"# マクロ経済ダッシュボード レポート ({date.today().isoformat()})",
        "",
        "データ出典: FRED (Federal Reserve Economic Data) https://fred.stlouisfed.org/",
        "",
    ]

    for metric in SERIES.values():
        lines.append(f"## {metric['label']}")
        for info in metric["countries"].values():
            try:
                s = fetch_series(info["id"])
            except DataFetchError as e:
                lines.append(f"- **{info['label']}**: 取得失敗 ({e})")
                continue

            if s.empty:
                lines.append(f"- **{info['label']}**: データなし")
                continue

            latest_date = s.index[-1].strftime("%Y-%m-%d")
            line = (
                f"- **{info['label']}**: {s.iloc[-1]:,.2f}{metric['unit']} "
                f"({latest_date}時点) — {_change_desc(s)}"
            )
            yoy = _yoy_desc(s)
            if yoy:
                line += f" / {yoy}"
            lines.append(line)
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    report = build_report()

    out_dir = PROJECT_ROOT / "reports"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{date.today().strftime('%Y%m%d')}_macro_report.md"
    out_path.write_text(report, encoding="utf-8")

    print(f"レポートを書き出しました: {out_path}")


if __name__ == "__main__":
    main()
