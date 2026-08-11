# 20260811_Stock_analysis

株価分析プロジェクト用のフォルダです。

## スコープ
このフォルダが Claude Code の作業スコープです。親フォルダ (`test_code`) 直下の他のプロジェクトフォルダ（例: `20260729_Test_code`）は無関係なので触らないでください（`../.claude/` のガードレール参照）。

## プロジェクト概要

FRED（Federal Reserve Economic Data）APIを使った日本/米国マクロ経済ダッシュボード（Streamlit製）。
政策金利・CPI・失業率・ドル円・株価指数（日経平均/S&P500）を日米比較で表示する。個別銘柄は扱わない。

- 使用言語/ライブラリ: Python, Streamlit, fredapi, pandas, plotly, python-dotenv（`requirements.txt`）
- 起動方法: `streamlit run app.py`（要 `.env` に `FRED_API_KEY`。`.env.example` 参照）
- データはローカルSQLite DB（`data/macro_dashboard.sqlite3`）経由でのみダッシュボードに渡る。
  FREDへの実アクセスは管理者ページの「DB更新」ボタンを押したときだけ発生する。
- ディレクトリ構成:
  - `app.py` — エントリーポイント。`st.navigation` でページの並び順・表示名を一元管理（管理者ページは常に最後）
  - `views/home.py` — 市場データサマリ(トップページ)。全指標の最新値をDBから一覧表示
  - `views/{policy_rate,cpi,unemployment,fx,stock_index}.py` — 指標ごとの時系列詳細ページ（薄いラッパー、`src/charts.py` を呼ぶだけ）
  - `views/admin.py` — 管理者ページ。FREDから取得しDBへ保存する唯一の入口
  - `src/config.py` — 指標とFRED系列IDの対応表（`SERIES`）。新指標追加はここが起点
  - `src/data_fetcher.py` — FREDへの実アクセス(管理者ページの更新時のみ呼ばれる)
  - `src/db.py` — SQLiteへの保存・読み出し・一括更新（`refresh_all`）
  - `src/charts.py` — 詳細ページの共通描画処理（DBを読む）
- git remote: `github.com/kazuchiiba/Market_Analysis_Tools`（pushはユーザーの明示指示があるときのみ）

## メモ

- 2026-08-11: 新指標追加・Markdownレポート生成を支援するスキルを追加（`.claude/skills/macro-dashboard/`）。
  手順は同スキルの `SKILL.md` / `references/add_indicator.md` を参照。
