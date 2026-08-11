"""指標とFRED(Federal Reserve Economic Data)系列IDの対応表。

新しい指標や国を追加したい場合は、この辞書に項目を追加するだけでよい。
Home.py / pages/*.py はこの定義を読んで自動的に画面を組み立てる。
"""

SERIES = {
    "policy_rate": {
        "label": "政策金利",
        "unit": "%",
        "page": "views/policy_rate.py",
        "dual_axis": False,
        "countries": {
            "japan": {"id": "IRSTCB01JPM156N", "label": "日本(無担保コールレート翌日物)"},
            "us": {"id": "FEDFUNDS", "label": "アメリカ(FF実効金利)"},
        },
    },
    "cpi": {
        "label": "消費者物価指数(CPI)",
        "unit": "指数",
        "page": "views/cpi.py",
        "dual_axis": True,
        "countries": {
            "japan": {"id": "JPNCPIALLMINMEI", "label": "日本(CPI 全品目、2015年=100)"},
            "us": {"id": "CPIAUCSL", "label": "アメリカ(CPI 全項目、季節調整済、1982-84年=100)"},
        },
    },
    "unemployment": {
        "label": "失業率",
        "unit": "%",
        "page": "views/unemployment.py",
        "dual_axis": False,
        "countries": {
            "japan": {"id": "LRHUTTTTJPM156S", "label": "日本(完全失業率)"},
            "us": {"id": "UNRATE", "label": "アメリカ(失業率)"},
        },
    },
    "fx": {
        "label": "ドル円",
        "unit": "円",
        "page": "views/fx.py",
        "dual_axis": False,
        "countries": {
            "usdjpy": {"id": "DEXJPUS", "label": "USD/JPY"},
        },
    },
    "index": {
        "label": "株価Index",
        "unit": "pt",
        "page": "views/stock_index.py",
        "dual_axis": True,
        "countries": {
            "japan": {"id": "NIKKEI225", "label": "日経平均株価"},
            "us": {"id": "SP500", "label": "S&P500"},
        },
    },
}

# キャッシュの有効期限(秒)。この時間以内に取得済みならFREDへ再アクセスしない。
CACHE_TTL_SECONDS = 6 * 60 * 60  # 6時間
