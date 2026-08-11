# 新しい指標をダッシュボードに追加する手順

このプロジェクトは「指標定義を1箇所(`src/config.py`)に追加し、薄いページファイルを1つ作る」だけで
新指標が Home 一覧・詳細ページ・キャッシュ更新ボタンすべてに反映されるように設計されている。
`src/charts.py` や `Home.py` のロジックは触らない。

## 手順

1. **FREDで系列(series) IDを探す**
   https://fred.stlouisfed.org/ で指標名を検索し、系列ページを開く。URL末尾
   (例: `https://fred.stlouisfed.org/series/UNRATE` なら `UNRATE`)が系列IDになる。

2. **`src/config.py` の `SERIES` にエントリを追加する**

   ```python
   "new_metric_key": {
       "label": "指標の表示名",
       "unit": "%",  # 単位。無ければ ""
       "page": "pages/6_新指標名.py",
       "dual_axis": False,  # 日米でスケールが大きく異なる場合は True
       "countries": {
           "japan": {"id": "FREDの系列ID", "label": "日本(補足)"},
           "us": {"id": "FREDの系列ID", "label": "アメリカ(補足)"},
       },
   },
   ```

   - `countries` は1カ国のみでもよい(例: 既存の `fx` は `usdjpy` のみ)。
   - キー名(`new_metric_key`)は英語スネークケースで、他と重複しないもの。

3. **`pages/` に薄いページファイルを作成する**

   ファイル名は `pages/<既存最大の連番+1>_<表示名>.py`(先頭数字がサイドバーの表示順)。
   中身は既存ページ(例: `pages/1_政策金利.py`)と同じ形。

   ```python
   import streamlit as st

   from src.charts import render_metric_detail_page

   st.set_page_config(page_title="○○の推移", page_icon="📈", layout="wide")
   render_metric_detail_page("new_metric_key")
   ```

   `page_title` は好きな文言でよいが、`render_metric_detail_page` に渡すキーは
   手順2で `SERIES` に追加したキーと一致させること。

4. **動作確認**

   ```
   streamlit run Home.py
   ```

   Home画面に新しいカードが表示され、「推移を見る →」から詳細ページに遷移できれば完了。
   `FRED_API_KEY` が未設定だとデータ取得でエラーになるので、`.env.example` を参考に `.env` を用意する。

## 単位・スケールについて

- `dual_axis: True` は、日米で単位やスケールが大きく異なる指標(例: CPI指数、株価指数)で
  左右の軸を分けて見やすくするためのオプション。数値の桁がだいたい同じなら `False` でよい。
