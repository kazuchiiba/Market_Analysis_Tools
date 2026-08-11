import streamlit as st

from src.charts import render_metric_detail_page

st.set_page_config(page_title="政策金利の推移", page_icon="📈", layout="wide")
render_metric_detail_page("policy_rate")
