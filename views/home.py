"""市場データサマリ(フロントページ)。

各指標(政策金利・CPI・失業率・ドル円・株価Index)の最新値を一覧表示する。
各行の「推移を見る →」から、対応する時系列推移ページに遷移できる。

表示データは常にローカルDBから読む(FREDへは直接アクセスしない)。
データの取得・更新は「管理者ページ」から行う。
"""

import streamlit as st

from src import db
from src.config import SERIES

st.set_page_config(page_title="市場データサマリ", page_icon="📊", layout="wide")

st.title("📊 市場データサマリ")
st.caption("日本 / アメリカ マクロ経済ダッシュボード ー データ出典: FRED (Federal Reserve Economic Data)")
st.page_link("views/admin.py", label="🛠️ データを更新する(管理者ページへ)")

st.divider()

db_is_empty = all(db.load_latest(sid)[1] is None for sid in db.all_series_ids())
if db_is_empty:
    st.info("DBにデータがまだありません。まず管理者ページから「DB更新」を実行してください。")

for metric_key, metric in SERIES.items():
    with st.container(border=True):
        header_col, link_col = st.columns([5, 1])
        header_col.subheader(metric["label"])
        link_col.page_link(metric["page"], label="推移を見る →", use_container_width=True)

        cols = st.columns(len(metric["countries"]))
        for col, (country_key, info) in zip(cols, metric["countries"].items()):
            date, value = db.load_latest(info["id"])
            if value is None:
                col.warning(f"{info['label']}: データがありません")
                continue
            col.metric(
                label=info["label"],
                value=f"{value:,.2f}{metric['unit']}",
                help=f"データ時点: {date.strftime('%Y-%m-%d')}",
            )

st.divider()
st.caption("左のサイドバー、または各カードの「推移を見る →」から時系列推移ページに移動できます。")
