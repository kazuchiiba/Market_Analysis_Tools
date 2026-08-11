"""指標の時系列グラフ・詳細ページの共通描画処理。

pages/*.py はそれぞれ `render_metric_detail_page("<metric_key>")` を呼ぶだけでよい。
表示内容(タイトル・最新値・グラフ・生データ表)はこのモジュールに集約している。

データは常にローカルDB(src/db.py)から読む。FREDへのアクセスは行わない
(FREDから最新化したい場合は管理者ページの「DB更新」ボタンを使う)。
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src import db
from src.config import SERIES


def render_metric_detail_page(metric_key: str) -> None:
    """指標1つ分の詳細ページ(最新値・時系列グラフ・生データ)を描画する。"""
    metric = SERIES[metric_key]
    countries = metric["countries"]

    st.title(f"📈 {metric['label']}の推移")
    st.caption("データ出典: FRED (Federal Reserve Economic Data)。表示内容はローカルDBの保存値です。")
    st.page_link("views/admin.py", label="🛠️ データを最新化する(管理者ページへ)")

    series_map: dict[str, pd.Series] = {}
    for country_key, info in countries.items():
        series_map[country_key] = db.load_series(info["id"])

    if all(s.empty for s in series_map.values()):
        st.warning("DBにデータがまだありません。管理者ページから「DB更新」を実行してください。")
        st.page_link("views/home.py", label="← 市場データサマリに戻る")
        return

    # 最新値
    cols = st.columns(len(series_map))
    for col, (country_key, s) in zip(cols, series_map.items()):
        label = countries[country_key]["label"]
        if s.empty:
            col.warning(f"{label}: データがありません")
            continue
        col.metric(
            label=label,
            value=f"{s.iloc[-1]:,.2f}{metric['unit']}",
            help=f"データ時点: {s.index[-1].strftime('%Y-%m-%d')}",
        )

    # 時系列グラフ(スケールが大きく異なる指標は2軸表示にする)
    dual_axis = bool(metric.get("dual_axis")) and len(series_map) > 1
    fig = make_subplots(specs=[[{"secondary_y": True}]]) if dual_axis else go.Figure()

    for i, (country_key, s) in enumerate(series_map.items()):
        if s.empty:
            continue
        trace = go.Scatter(x=s.index, y=s.values, mode="lines", name=countries[country_key]["label"])
        if dual_axis:
            fig.add_trace(trace, secondary_y=(i == 1))
        else:
            fig.add_trace(trace)

    fig.update_layout(
        hovermode="x unified",
        xaxis_title="日付",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40),
        height=500,
    )
    if not dual_axis:
        fig.update_yaxes(title_text=f"{metric['label']} ({metric['unit']})")

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("生データを表示"):
        combined = pd.DataFrame(
            {countries[k]["label"]: v for k, v in series_map.items() if not v.empty}
        ).sort_index(ascending=False)
        st.dataframe(combined, use_container_width=True)

    with st.expander("DB更新状況"):
        for country_key, info in countries.items():
            status = db.get_status(info["id"])
            label = countries[country_key]["label"]
            if status["last_updated_at"] is None:
                st.write(f"- {label}: 未更新")
            elif status["last_error"]:
                st.write(f"- {label}: 最終試行 {status['last_updated_at']}(エラー: {status['last_error']})")
            else:
                st.write(f"- {label}: 最終更新 {status['last_updated_at']}")

    st.page_link("views/home.py", label="← 市場データサマリに戻る")
