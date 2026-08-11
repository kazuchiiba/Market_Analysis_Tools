"""マクロ経済ダッシュボード エントリーポイント。

起動方法: streamlit run app.py

ページの並び順・サイドバー表示名はここで一元管理する。
管理者ページは意図的に一番最後に配置している(通常利用の動線から離すため)。
"""

import streamlit as st

home = st.Page("views/home.py", title="市場データサマリ", icon="📊", default=True)
policy_rate = st.Page("views/policy_rate.py", title="政策金利", icon="📈")
cpi = st.Page("views/cpi.py", title="消費者物価指数", icon="📈")
unemployment = st.Page("views/unemployment.py", title="失業率", icon="📈")
fx = st.Page("views/fx.py", title="ドル円", icon="📈")
stock_index = st.Page("views/stock_index.py", title="株価Index", icon="📈")
admin = st.Page("views/admin.py", title="管理者ページ", icon="🛠️")

pg = st.navigation([home, policy_rate, cpi, unemployment, fx, stock_index, admin])
pg.run()
