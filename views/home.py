"""市場データサマリ(フロントページ)。

ヒーロー(JS/CSSアニメーション付き、st.components.v1.html)+ 市場データサマリの2段構成。
各行の「推移を見る →」から、対応する時系列推移ページに遷移できる。

表示データは常にローカルDBから読む(FREDへは直接アクセスしない)。
データの取得・更新は「管理者ページ」から行う。

デザイン/コンテンツ仕様は DESIGN.md / CONTENTS.md を参照。
"""

from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

from src import db
from src.config import SERIES
from src.theme import country_accent, inject_theme, render_hero

st.set_page_config(page_title="市場データサマリ｜MACRO SIGNALS", page_icon="📊", layout="wide")

inject_theme()

# --- ヒーロー用の動的テキストを組み立てる (CONTENTS.md 4章) ---
all_ids = db.all_series_ids()
last_updates = [db.get_status(sid)["last_updated_at"] for sid in all_ids]
last_updates = [u for u in last_updates if u]

if not last_updates:
    updated_text = "NO DATA YET"
else:
    latest = max(last_updates)
    try:
        dt = datetime.fromisoformat(latest)
        updated_text = dt.strftime("%Y.%m.%d %H:%M") + " UTC"
    except ValueError:
        updated_text = latest

db_is_empty = all(db.load_latest(sid)[1] is None for sid in all_ids)
data_status = "DATA STATUS · LIVE" if not db_is_empty else "DATA STATUS · DELAYED"

hero_html = render_hero(updated_text=updated_text, data_status=data_status)
components.html(hero_html, height=560, scrolling=False)

# --- 市場データサマリ (CONTENTS.md 5章) ---
st.markdown(
    """
    <div style="margin-top: 8px;">
        <div style="font-size:11px; letter-spacing:0.14em; color:#FF3D18; font-weight:700;">
            CURRENT SNAPSHOT
        </div>
        <div style="font-size:1.6rem; font-weight:900; font-family:'Roboto Condensed','Noto Sans JP',sans-serif; margin-top:4px;">
            市場データサマリ
        </div>
        <div style="color:#6B6F70; font-size:0.9rem; margin-top:2px;">
            日米の政策金利・物価・雇用・為替・株価を、最新公表値で比較します。
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.page_link("views/admin.py", label="🛠️ データを更新する(管理者ページへ)")

st.divider()

if db_is_empty:
    st.info("DBにデータがまだありません。まず管理者ページから「DB更新」を実行してください。")

for metric_key, metric in SERIES.items():
    header_col, link_col = st.columns([5, 1])
    header_col.markdown(f"**{metric['label']}**")
    link_col.page_link(metric["page"], label="推移を見る →", use_container_width=True)

    cols = st.columns(len(metric["countries"]))
    for col, (country_key, info) in zip(cols, metric["countries"].items()):
        date, value = db.load_latest(info["id"])
        accent = country_accent(country_key)
        with col:
            if value is None:
                st.warning(f"{info['label']}: データがありません")
                continue
            st.markdown(
                f"""
                <div style="text-align:center; padding: 12px 8px;">
                    <div class="macro-value" style="font-size:2.1rem; font-weight:700; color:{accent};">
                        {value:,.2f}<span style="font-size:1.1rem; font-weight:500;">{metric['unit']}</span>
                    </div>
                    <div style="font-size:0.82rem; color:#4A4D4E; margin-top:4px;">
                        {info['label']}
                    </div>
                    <div style="font-size:0.72rem; color:#9A9C9C; margin-top:2px;">
                        データ時点 {date.strftime('%Y-%m-%d')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown(f"<hr style='border-top:1px solid #C9CBC7; margin: 4px 0 20px 0;' />", unsafe_allow_html=True)

st.caption("左のサイドバー、または各カードの「推移を見る →」から時系列推移ページに移動できます。")
