"""サイト全体で共有するデザイントークンとCSS注入ヘルパー。

DESIGN.md の配色・タイポグラフィを全ページへ適用するための共通モジュール。
ヒーロー(市場データサマリのみ)は render_hero() で組み立てたHTMLを
st.components.v1.html() に渡して埋め込む(iframe内で完結する本物のJS/CSSアニメーション)。
それ以外のページは inject_theme() を先頭で呼ぶだけで配色・タイポグラフィが揃う。
"""

from __future__ import annotations

import html

import streamlit as st

# --- カラートークン (DESIGN.md 9章) ---
INK_BLACK = "#0B0D0E"
WARM_WHITE = "#F2F1EC"
NEAR_BLACK = "#121415"
SOFT_WHITE = "#F7F6F2"
JP_VERMILION = "#FF3D18"
US_BLUE = "#2D5BFF"
GRID_GRAY = "#C9CBC7"

_FONT_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2"
    "?family=Roboto+Condensed:wght@400;700&family=Noto+Sans+JP:wght@400;500;700;900&display=swap');"
)

_BASE_CSS = f"""
<style>
{_FONT_IMPORT}

html, body, [class*="css"] {{
    font-family: "Noto Sans JP", "Roboto Condensed", system-ui, sans-serif;
}}

/* 数値は桁がガタつかないようタブラー数字に統一 (DESIGN.md 10章) */
[data-testid="stMetricValue"], .macro-value {{
    font-variant-numeric: tabular-nums;
    font-family: "Roboto Condensed", "Noto Sans JP", system-ui, sans-serif;
}}

hr {{
    border-color: {GRID_GRAY} !important;
}}

a {{
    color: {JP_VERMILION};
}}

/* st.container(border=True) の角丸カードを、罫線ベースの区切りに寄せる (DESIGN.md 6章) */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 2px !important;
    border-color: {GRID_GRAY} !important;
}}
</style>
"""


def inject_theme() -> None:
    """全ページ共通の配色・タイポグラフィCSSを注入する。各ページの先頭で1回呼ぶ。"""
    st.markdown(_BASE_CSS, unsafe_allow_html=True)


def country_accent(country_key: str) -> str:
    """国キーからアクセントカラーを返す(日本=朱赤、アメリカ=ブルー、それ以外はグレー系)。"""
    key = country_key.lower()
    if "jp" in key or "japan" in key:
        return JP_VERMILION
    if "us" in key or "usa" in key:
        return US_BLUE
    return NEAR_BLACK


def render_hero(*, updated_text: str, data_status: str) -> str:
    """市場データサマリのヒーローHTML(st.components.v1.html に渡す文字列)を組み立てる。

    軌道線の描画アニメーション・データオーブの浮遊アニメーションはCSSのみで実装し、
    iframe内で完結させている(Streamlitの再実行と無関係に動き続ける)。
    """
    updated_text = html.escape(updated_text)
    data_status = html.escape(data_status)

    return """
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<style>
  @import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700;900&family=Noto+Sans+JP:wght@500;700;900&display=swap');

  * { box-sizing: border-box; }

  html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    background: __INK_BLACK__;
    overflow: hidden;
    font-family: "Noto Sans JP", "Roboto Condensed", system-ui, sans-serif;
  }

  .hero {
    position: relative;
    width: 100%;
    height: 100%;
    background:
      radial-gradient(circle at 78% 30%, rgba(255,61,24,0.16), transparent 42%),
      radial-gradient(circle at 22% 75%, rgba(45,91,255,0.16), transparent 46%),
      repeating-linear-gradient(0deg, rgba(247,246,242,0.04) 0px, rgba(247,246,242,0.04) 1px, transparent 1px, transparent 40px),
      repeating-linear-gradient(90deg, rgba(247,246,242,0.04) 0px, rgba(247,246,242,0.04) 1px, transparent 1px, transparent 40px),
      __INK_BLACK__;
    overflow: hidden;
  }

  .orbit-svg {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
  }

  .orbit-path {
    fill: none;
    stroke-width: 1.6;
    stroke-linecap: round;
    stroke-dasharray: 1400;
    stroke-dashoffset: 1400;
    animation: draw 1.8s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  }
  .orbit-path.jp { stroke: __JP_VERMILION__; opacity: 0.55; }
  .orbit-path.us { stroke: __US_BLUE__; opacity: 0.55; animation-delay: 0.25s; }

  @keyframes draw {
    to { stroke-dashoffset: 0; }
  }

  .orb {
    position: absolute;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: "Roboto Condensed", sans-serif;
    font-weight: 700;
    color: rgba(247,246,242,0.85);
    background: radial-gradient(circle at 32% 28%, rgba(255,255,255,0.20), rgba(18,20,21,0.05) 60%), rgba(247,246,242,0.06);
    border: 1px solid rgba(247,246,242,0.14);
    box-shadow: 0 12px 28px rgba(0,0,0,0.35);
    opacity: 0;
    animation: fadeIn 1s ease forwards, floaty 6s ease-in-out infinite;
  }
  @keyframes fadeIn { to { opacity: 1; } }
  @keyframes floaty {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-14px); }
  }

  .orb.jp { border-color: rgba(255,61,24,0.4); }
  .orb.us { border-color: rgba(45,91,255,0.4); }

  .o1 { width: 64px; height: 64px; font-size: 20px; top: 16%; left: 68%; animation-duration: 1s, 5.5s; animation-delay: 0.4s, 0s; }
  .o2 { width: 44px; height: 44px; font-size: 15px; top: 62%; left: 78%; animation-duration: 1s, 7s; animation-delay: 0.6s, 0.3s; }
  .o3 { width: 52px; height: 52px; font-size: 16px; top: 30%; left: 85%; animation-duration: 1s, 6.2s; animation-delay: 0.8s, 0.6s; }
  .o4 { width: 38px; height: 38px; font-size: 13px; top: 78%; left: 60%; animation-duration: 1s, 6.8s; animation-delay: 1s, 0.2s; }
  .o5 { width: 46px; height: 46px; font-size: 14px; top: 10%; left: 45%; animation-duration: 1s, 5.8s; animation-delay: 1.2s, 0.5s; }

  .content {
    position: relative;
    z-index: 2;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 4vw 5vw;
  }

  .eyebrow {
    color: __JP_VERMILION__;
    font-size: clamp(11px, 1.1vw, 14px);
    letter-spacing: 0.18em;
    font-weight: 700;
    margin: 0 0 14px 0;
    opacity: 0;
    animation: slideUp 0.7s ease 0.15s forwards;
  }

  h1.title {
    margin: 0;
    color: __SOFT_WHITE__;
    font-family: "Roboto Condensed", "Noto Sans JP", sans-serif;
    font-weight: 900;
    font-size: clamp(3.2rem, 11vw, 8.5rem);
    line-height: 0.86;
    letter-spacing: -0.01em;
    opacity: 0;
    animation: slideUp 0.8s ease 0.3s forwards;
  }

  .lead {
    margin: 22px 0 0 0;
    color: rgba(247,246,242,0.68);
    font-size: clamp(14px, 1.35vw, 18px);
    line-height: 1.6;
    max-width: 34ch;
    opacity: 0;
    animation: slideUp 0.8s ease 0.5s forwards;
  }

  .cta {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-top: 28px;
    width: fit-content;
    padding: 10px 18px;
    border: 1px solid rgba(247,246,242,0.4);
    color: __SOFT_WHITE__;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.04em;
    border-radius: 999px;
    opacity: 0;
    animation: slideUp 0.8s ease 0.65s forwards;
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .meta {
    position: absolute;
    right: 5vw;
    bottom: 4vw;
    z-index: 2;
    text-align: right;
    color: rgba(247,246,242,0.55);
    font-size: clamp(10px, 0.95vw, 12px);
    letter-spacing: 0.08em;
    line-height: 1.7;
    opacity: 0;
    animation: fadeIn 1s ease 0.9s forwards;
  }
  .meta .status-dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: __JP_VERMILION__;
    margin-right: 6px;
  }

  .legend {
    position: absolute;
    left: 5vw;
    top: 3vw;
    z-index: 2;
    display: flex;
    gap: 16px;
    font-size: 11px;
    color: rgba(247,246,242,0.55);
    letter-spacing: 0.08em;
  }
  .legend span.dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; }

  @media (prefers-reduced-motion: reduce) {
    .orbit-path, .orb, .eyebrow, .title, .lead, .cta, .meta {
      animation: none !important;
      opacity: 1 !important;
      stroke-dashoffset: 0 !important;
    }
  }
</style>
</head>
<body>
  <div class="hero">
    <svg class="orbit-svg" viewBox="0 0 1000 500" preserveAspectRatio="none" aria-hidden="true">
      <path class="orbit-path jp" d="M -50,380 C 150,300 300,420 480,340 S 780,180 1050,220" />
      <path class="orbit-path us" d="M -50,120 C 180,200 340,80 540,160 S 820,340 1050,300" />
    </svg>

    <div class="orb jp o1" aria-hidden="true">%</div>
    <div class="orb us o2" aria-hidden="true">$</div>
    <div class="orb jp o3" aria-hidden="true">CPI</div>
    <div class="orb us o4" aria-hidden="true">¥</div>
    <div class="orb jp o5" aria-hidden="true">RATE</div>

    <div class="legend" aria-hidden="true">
      <span><span class="dot" style="background: __JP_VERMILION__;"></span>JP</span>
      <span><span class="dot" style="background: __US_BLUE__;"></span>US</span>
    </div>

    <div class="content">
      <p class="eyebrow">JAPAN / UNITED STATES &middot; DAILY MACRO VIEW</p>
      <h1 class="title">MACRO<br/>SIGNALS</h1>
      <p class="lead">数字の変化から、経済の現在地を読む。<br/>日本とアメリカの主要指標を、ひとつの画面で。</p>
      <div class="cta">最新の指標を見る &darr;</div>
    </div>

    <div class="meta">
      <div><span class="status-dot"></span>__DATA_STATUS__</div>
      <div>UPDATED &middot; __UPDATED_TEXT__</div>
      <div>SOURCE &middot; FRED</div>
    </div>
  </div>
</body>
</html>
""".replace("__INK_BLACK__", INK_BLACK).replace("__JP_VERMILION__", JP_VERMILION).replace(
        "__US_BLUE__", US_BLUE
    ).replace("__SOFT_WHITE__", SOFT_WHITE).replace(
        "__DATA_STATUS__", data_status
    ).replace("__UPDATED_TEXT__", updated_text)
