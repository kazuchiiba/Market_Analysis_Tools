"""管理者ページ: FREDからデータを取得し、ローカルDBを更新する。

ダッシュボード本体(市場データサマリ / 各推移ページ)はここで作られたDBを読むだけで、
FREDへは直接アクセスしない。データを最新化したいときは、このページの
ボタンを押す。ナビゲーション上、常に一番最後に表示される(app.py参照)。
"""

import streamlit as st

from src import db
from src.config import SERIES

st.set_page_config(page_title="管理者ページ", page_icon="🛠️", layout="wide")

st.title("🛠️ 管理者ページ: DB更新")
st.caption("FREDから最新データを取得し、ローカルDB(data/macro_dashboard.sqlite3)へ保存します。")

if st.button("🔄 FREDからDBを更新", type="primary"):
    with st.spinner("FREDから取得しDBへ保存しています..."):
        results = db.refresh_all()

    ok_count = sum(1 for success, _ in results.values() if success)
    ng_count = len(results) - ok_count
    if ng_count == 0:
        st.success(f"全 {ok_count} 系列の更新に成功しました。")
    else:
        st.warning(f"{ok_count} 系列は成功、{ng_count} 系列は失敗しました。詳細は下の一覧を確認してください。")

    for series_id, (success, error) in results.items():
        if not success:
            st.error(f"{series_id}: {error}")

st.divider()
st.subheader("現在のDB状況")

rows = []
for metric in SERIES.values():
    for info in metric["countries"].values():
        series_id = info["id"]
        status = db.get_status(series_id)
        date, value = db.load_latest(series_id)
        rows.append(
            {
                "指標": metric["label"],
                "国/系列": info["label"],
                "FRED系列ID": series_id,
                "DB内の最新データ日": date.strftime("%Y-%m-%d") if date is not None else "-",
                "DB内の最新値": f"{value:,.2f}" if value is not None else "-",
                "最終更新試行(UTC)": status["last_updated_at"] or "未実行",
                "最終エラー": status["last_error"] or "",
            }
        )

st.dataframe(rows, use_container_width=True, hide_index=True)

st.divider()
st.page_link("views/home.py", label="← 市場データサマリに戻る")
