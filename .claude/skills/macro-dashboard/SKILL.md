---
name: macro-dashboard
description: このプロジェクト(FRED × Streamlit の日本/米国マクロ経済ダッシュボード)で、新しい経済指標をダッシュボードに追加する作業、および現在のデータからMarkdown分析レポートを生成する作業を支援する。「指標を追加して」「〇〇のページを作って」「マクロ経済レポートを作って」「最新の指標をまとめて」等のリクエスト時に使う。個別銘柄(yfinance等)は対象外。
---

# マクロ経済ダッシュボード運用スキル

本プロジェクトは [FRED (Federal Reserve Economic Data)](https://fred.stlouisfed.org/) API と Streamlit を使った日本/米国マクロ経済ダッシュボード。政策金利・CPI・失業率・ドル円・株価指数(日経平均/S&P500)を扱う。

アーキテクチャの要点(詳細を読む前に把握しておくこと):

- `src/config.py` の `SERIES` 辞書が唯一の定義元。指標ごとに `label` / `unit` / `page` / `dual_axis` / `countries`(国ごとのFRED系列ID)を持つ。
- `src/data_fetcher.py` の `fetch_series()` がFRED取得とキャッシュ(`data_cache/`, TTL 6時間)を担当。APIキー未設定でもキャッシュがあれば動く。
- `src/charts.py` の `render_metric_detail_page()` が、最新値カード・時系列グラフ・生データ表・更新ボタンを丸ごと描画する共通処理。
- `pages/*.py` は `render_metric_detail_page("<metric_key>")` を呼ぶだけの薄いラッパー。
- `Home.py` は `SERIES` を走査して一覧カードを自動生成するので、新指標を追加してもここは触らなくてよい。

## 1. 新しい指標をダッシュボードに追加する

手順は [references/add_indicator.md](references/add_indicator.md) を参照。要点は、`src/config.py` の `SERIES` に1エントリ追加し、`pages/` に薄いラッパーページを1つ作るだけ。グラフ描画・キャッシュ更新・Home一覧表示は自動で対応する。

## 2. 最新データからMarkdown分析レポートを作る

`scripts/generate_report.py` を実行すると、`SERIES` 全指標の最新値・前回比・前年同期比をまとめた Markdown を `reports/YYYYMMDD_macro_report.md` に書き出す。

```
python .claude/skills/macro-dashboard/scripts/generate_report.py
```

- `FRED_API_KEY` が `.env` に未設定でも、`data_cache/` に既存キャッシュがあればそれを使って動く(なければ取得失敗した指標だけレポートに「取得失敗」と記載される)。
- 依存ライブラリは `requirements.txt` にある `pandas` / `python-dotenv` / `fredapi` のみで足りる。
- 生成後のMarkdownに考察コメントを足したい場合は、そのまま直接編集してよい。

## 注意事項

- データソースはFREDのみ。個別銘柄データ(yfinance等)はこのスキルの対象外。
- git remote(`Market_Analysis_Tools`)への `git push` は、ユーザーから明示的な指示があるときのみ行う。
