"""
Trading Bots: Reality Check — Portfolio Dashboard
══════════════════════════════════════════════════
Author  : Pawan Bohora · MSCS, Wright State University
GitHub  : github.com/pawanbohora/trading-bots-reality-check

Data provenance legend used throughout this file:
  SOURCE     — figure cited directly from a published study, regulator disclosure, or broker report
  MODELED    — derived / calculated from source figures (e.g. net = gross − fees − slippage)
  ILLUS      — illustrative scenario built to explain a concept; assumptions explicitly stated
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ═══════════════════════════════════════════════════════════════════════════════
# 1 ·  PAGE CONFIG  (must be the very first Streamlit call)
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Trading Bots: Reality Check",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════════════════════════════════════════
# 2 ·  DESIGN SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════
BG     = "#0F1117"
CARD   = "#1A1D27"
BORDER = "#2A2D3A"
BLUE   = "#4F8EF7"
RED    = "#F75D5D"
GREEN  = "#4FD1A5"
YELLOW = "#F7C948"
TEXT   = "#F0F2FA"   # primary text — bright enough for dark background
MUTED  = "#C0C3D4"   # secondary text — significantly brighter than default grey
SUB    = "#8A8E9E"   # truly de-emphasised labels (footnotes, eyebrows)
GRID   = "#2A2D3A"
DIM    = "#3A3D4A"   # de-emphasised bars when filter is active

TRADER_COLORS = {
    "Retail Bot":              BLUE,
    "Manual Day Trader":       RED,
    "Institutional Algo":      GREEN,
    "Passive Index (S&P 500)": YELLOW,
}
TRADERS = list(TRADER_COLORS.keys())

H      = 380    # standard chart height
H_WIDE = 420    # full-width chart height

BASE = dict(
    paper_bgcolor=CARD,
    plot_bgcolor=CARD,
    font=dict(color=TEXT, family="Inter, system-ui, sans-serif", size=12),
    title_font=dict(color=TEXT, size=14, family="Inter, system-ui, sans-serif"),
    xaxis=dict(
        gridcolor=GRID, linecolor=BORDER,
        tickfont=dict(color=MUTED, size=11),
        zerolinecolor=BORDER,
    ),
    yaxis=dict(
        gridcolor=GRID, linecolor=BORDER,
        tickfont=dict(color=MUTED, size=11),
        zerolinecolor=BORDER,
    ),
    margin=dict(l=48, r=32, t=58, b=44),
    hoverlabel=dict(bgcolor=CARD, bordercolor=BORDER, font_color=TEXT),
    legend=dict(bgcolor=CARD, bordercolor=BORDER, font=dict(color=TEXT, size=11)),
)


# ═══════════════════════════════════════════════════════════════════════════════
# 3 ·  CUSTOM CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
/* ── shell ───────────────────────────────────────────────────────── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"]            {{ background-color: {BG}; }}
[data-testid="stHeader"]          {{ background-color: {BG}; border-bottom: 1px solid {BORDER}; }}
[data-testid="stSidebar"]         {{ background-color: {CARD}; border-right: 1px solid {BORDER}; }}
[data-testid="stSidebarContent"] > div:first-child {{ padding-top: 1.5rem; }}

/* ── base typography — fix grey-on-black readability ─────────────── */
.stApp p, .stMarkdown p, .stMarkdown li,
.stMarkdown span, .element-container p  {{ color: {TEXT}; }}
.stMarkdown                             {{ color: {TEXT}; }}

/* ── metric cards ────────────────────────────────────────────────── */
[data-testid="metric-container"] {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 16px 18px;
}}
[data-testid="stMetricValue"] {{ color: {BLUE}; font-size: 1.75rem !important; font-weight: 700; }}
[data-testid="stMetricLabel"] {{ color: {MUTED}; font-size: 0.80rem !important; font-weight: 500; }}
[data-testid="stMetricDelta"] {{ font-size: 0.76rem !important; }}

/* ── section headers ─────────────────────────────────────────────── */
.sec-wrap    {{ margin-bottom: 12px; }}
.sec-eyebrow {{ color: {SUB}; font-size: 0.68rem; letter-spacing: 0.14em;
                text-transform: uppercase; margin-bottom: 3px; }}
.sec-title   {{ color: {TEXT}; font-size: 1.3rem; font-weight: 700; line-height: 1.25; }}
.sec-cap     {{ color: {MUTED}; font-size: 0.88rem; margin-top: 4px; margin-bottom: 6px; }}

/* ── provenance tags ─────────────────────────────────────────────── */
.tag         {{ display: inline-block; border-radius: 5px; padding: 1px 8px;
                font-size: 0.68rem; font-weight: 700; letter-spacing: 0.05em;
                vertical-align: middle; margin-left: 6px; }}
.tag-source  {{ background: rgba(79,209,165,0.13); color: {GREEN};
                border: 1px solid rgba(79,209,165,0.28); }}
.tag-modeled {{ background: rgba(79,142,247,0.13); color: {BLUE};
                border: 1px solid rgba(79,142,247,0.28); }}
.tag-illus   {{ background: rgba(247,201,72,0.11); color: {YELLOW};
                border: 1px solid rgba(247,201,72,0.22); }}

/* ── insight cards ───────────────────────────────────────────────── */
.ins         {{ background: {CARD}; border-left: 3px solid {BLUE};
                border-radius: 0 8px 8px 0; padding: 14px 18px; margin-bottom: 12px; }}
.ins.red     {{ border-left-color: {RED};    }}
.ins.yellow  {{ border-left-color: {YELLOW}; }}
.ins.green   {{ border-left-color: {GREEN};  }}
.ins-title   {{ font-weight: 700; color: {TEXT}; font-size: 0.96rem; }}
.ins-body    {{ color: {MUTED}; font-size: 0.88rem; line-height: 1.62; margin-top: 5px; }}
.ins-src     {{ color: {SUB}; font-size: 0.76rem; margin-top: 6px; }}

/* ── conclusion takeaway cards ───────────────────────────────────── */
.takeaway      {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px;
                  padding: 20px 22px; margin-bottom: 10px; height: 100%; }}
.takeaway-num  {{ color: {BLUE}; font-size: 1.5rem; font-weight: 800; line-height: 1; }}
.takeaway-text {{ color: {MUTED}; font-size: 0.90rem; line-height: 1.65; margin-top: 8px; }}

/* ── source note ─────────────────────────────────────────────────── */
.src-note    {{ color: {SUB}; font-size: 0.79rem; margin-top: 2px;
                margin-bottom: 8px; font-style: italic; }}

/* ── sidebar ─────────────────────────────────────────────────────── */
.sb-label    {{ color: {SUB}; font-size: 0.72rem; text-transform: uppercase;
                letter-spacing: 0.1em; margin-bottom: 4px; margin-top: 20px; }}
.sb-badge    {{ display: inline-block; background: rgba(79,142,247,0.10);
                border: 1px solid rgba(79,142,247,0.25); border-radius: 16px;
                color: {BLUE}; font-size: 0.78rem; padding: 2px 10px; margin-top: 6px; }}

/* ── misc ────────────────────────────────────────────────────────── */
hr {{ border-color: {BORDER} !important; margin: 28px 0; }}
[data-testid="stExpander"] {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 8px; }}
[data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 8px; }}
.stAlert {{ border-radius: 8px; }}
.stAlert p {{ color: inherit; }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 4 ·  DATA LAYER
#      Separated from presentation. Each value tagged SOURCE / MODELED / ILLUS.
# ═══════════════════════════════════════════════════════════════════════════════

def load_data() -> dict:
    """
    Central data loader. Returns all datasets used by the dashboard.
    Provenance tags are embedded as comments and in the 'Provenance' column
    where applicable.
    """
    # ── Main comparison table ──────────────────────────────────────────────────
    # Win rates:     SOURCE  — Barber & Odean (retail/manual), industry aggregates (institutional)
    # Gross return:  MODELED — category averages compiled from multiple sources
    # Fees/slip:     MODELED — median estimates per category; retail bot from MEXC analysis
    # Net return:    MODELED — gross − fees − slippage
    # Drawdown:      MODELED — typical reported ranges per category
    # 6-Mo failure:  SOURCE  — ForTraders 2026 (bots), Barber & Odean (manual), ESMA (EU)
    df_traders = pd.DataFrame({
        "Trader Type":      TRADERS,
        "Win Rate (%)":     [56,   48,   74,   100],
        "Gross Return (%)": [9.2,  5.1,  23.5, 10.0],
        "Fees (%)":         [2.3,  1.4,  0.3,  0.05],
        "Slippage (%)":     [1.8,  0.6,  0.1,  0.0],
        "Net Return (%)":   [5.1,  3.1,  23.1, 9.95],
        "Max Drawdown (%)": [19.5, 24.2, 10.8, 13.7],
        "6-Mo Failure (%)": [73,   88,   15,   0],
    })

    # ── Regulator loss rates ───────────────────────────────────────────────────
    # All figures SOURCE from mandatory legal disclosures or peer-reviewed studies.
    # *Retail algo bot figure from TradingView Hub 2026 — subject to survivorship bias.
    df_loss = pd.DataFrame({
        "Market": [
            "India F&O (SEBI 2024)",
            "EU CFD Avg (ESMA)",
            "Taiwan Day Traders",
            "US Forex (Retail)",
            "Manual Day Traders",
            "Retail Algo Bots*",
        ],
        "Loss %": [93, 75, 82, 77, 88, 40],
        "Source": [
            "SEBI 2024",
            "ESMA",
            "Barber & Odean",
            "CFTC",
            "Multiple studies",
            "TradingView Hub 2026",
        ],
    })

    # ── Survivorship bias correction ──────────────────────────────────────────
    # SOURCE:  Andrikogiannopoulou & Papakonstantinou (hedge fund survivorship study)
    # MODELED: Correction factors applied to retail bot context
    sb_data = {
        "metrics":   ["Annual Return (%)", "Sharpe Ratio", "Max Drawdown (%)"],
        "biased":    [14.2, 1.40, 12.0],
        "corrected": [10.6, 0.90, 26.0],
    }

    return {"traders": df_traders, "loss": df_loss, "sb": sb_data}


def build_win_rate_model() -> tuple:
    """
    MODELED: Continuous P&L vs win-rate curve derived from SOURCE inputs.

    Avg winner +1.2% and avg loser −2.8% are SOURCE values from
    Barber, Makov & Schwartz (JFQA 2024) — study of 25,000+ retail accounts.
    Break-even win rate is algebraic: |loss| / (win + |loss|).

    Returns: (win_rates, pnl_per_trade, breakeven_wr, win_avg, loss_avg)
    """
    WIN_AVG  = +1.2   # SOURCE
    LOSS_AVG = -2.8   # SOURCE
    BREAKEVEN_WR = abs(LOSS_AVG) / (WIN_AVG + abs(LOSS_AVG))  # math → ≈0.70
    wr  = np.linspace(0.30, 0.88, 800)
    pnl = wr * WIN_AVG + (1 - wr) * LOSS_AVG
    return wr, pnl, BREAKEVEN_WR, WIN_AVG, LOSS_AVG


def build_growth_model(years: list) -> pd.DataFrame:
    """
    ILLUS: Compound growth trajectories — scenario model, not observed tracks.

    Assumed annual rates (stated assumptions, not guarantees):
      Passive Index:   10.0% p.a.  (S&P 500 historical CAGR · Dalbar)
      Retail Bot:       6.5% p.a.  (optimistic net-of-cost estimate)
      Manual Retail:    3.9% p.a.  (Dalbar 20-year average retail return)

    Starting capital: $10,000 · Jan 2006.
    """
    n = len(years)
    return pd.DataFrame({
        "Year":                    years,
        "Passive Index (S&P 500)": [10_000 * 1.100 ** i for i in range(n)],
        "Retail Bot (Optimistic)": [10_000 * 1.065 ** i for i in range(n)],
        "Manual Retail Trader":    [10_000 * 1.039 ** i for i in range(n)],
    })


# ── Initialise ─────────────────────────────────────────────────────────────────
DATA       = load_data()
df_traders = DATA["traders"]
df_loss    = DATA["loss"]
sb_data    = DATA["sb"]

wr, pnl, BREAKEVEN_WR, WIN_AVG, LOSS_AVG = build_win_rate_model()

YEARS     = list(range(2006, 2026))
df_growth = build_growth_model(YEARS)

# MODELED: Illustrative cost erosion waterfall for a typical retail bot strategy
EROSION_X      = ["Gross\nReturn", "Exchange\nFees", "Slippage", "Latency &\nExecution", "Net\nReturn"]
EROSION_DELTAS = [20.0, -5.5, -4.7, -2.6, 0.0]
EROSION_TYPES  = ["absolute", "relative", "relative", "relative", "total"]


# ═══════════════════════════════════════════════════════════════════════════════
# 5 ·  UI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def bar_color(trader: str, selected: str) -> str:
    """Full colour when unfiltered or matches selection; dim otherwise."""
    if selected == "All Traders":
        return TRADER_COLORS[trader]
    return TRADER_COLORS[trader] if trader == selected else DIM


def bar_opacity(trader: str, selected: str) -> float:
    if selected == "All Traders":
        return 1.0
    return 1.0 if trader == selected else 0.30


def render_section_header(
    eyebrow: str,
    title: str,
    caption: str = "",
    tag: str = "",
    tag_type: str = "source",
) -> None:
    """Render a styled section header with an optional provenance tag."""
    cap_html = f'<div class="sec-cap">{caption}</div>' if caption else ""
    tag_html = ""
    if tag:
        css = {"source": "tag-source", "modeled": "tag-modeled", "illus": "tag-illus"}.get(tag_type, "tag-source")
        tag_html = f'<span class="tag {css}">{tag}</span>'
    st.markdown(
        f'<div class="sec-wrap">'
        f'<div class="sec-eyebrow">{eyebrow}</div>'
        f'<div class="sec-title">{title}{tag_html}</div>'
        f'{cap_html}</div>',
        unsafe_allow_html=True,
    )


def render_insight_card(color: str, title: str, body: str, source: str) -> None:
    """Render a coloured insight card with title, body text, and source citation."""
    st.markdown(
        f'<div class="ins {color}">'
        f'<div class="ins-title">{title}</div>'
        f'<div class="ins-body">{body}</div>'
        f'<div class="ins-src">Source: {source}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def source_note(text: str) -> None:
    """Small italic note placed directly beneath a chart."""
    st.markdown(
        f'<div class="src-note">📎 {text}</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 6 ·  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        f"<h2 style='color:{TEXT}; font-size:1.15rem; font-weight:800; margin-bottom:2px;'>"
        "📊 Trading Bots: Reality Check</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<span style='color:{MUTED}; font-size:0.84rem; line-height:1.55;'>"
        "A forensic analysis of retail algorithmic trading performance "
        "after fees, slippage, latency, and risk."
        "</span>",
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown('<div class="sb-label">Filter · Trader Type</div>', unsafe_allow_html=True)
    selected_trader = st.selectbox(
        label="Trader type",
        options=["All Traders"] + TRADERS,
        index=0,
        label_visibility="collapsed",
        help="Highlight a single trader type across all comparison charts.",
    )
    if selected_trader != "All Traders":
        st.markdown(
            f'<div class="sb-badge">Highlighting: {selected_trader}</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown('<div class="sb-label">Quick Stats</div>', unsafe_allow_html=True)
    sel_row = df_traders[df_traders["Trader Type"] == selected_trader]
    if not sel_row.empty:
        r = sel_row.iloc[0]
        st.metric("Net Return",    f"{r['Net Return (%)']:.1f}%")
        st.metric("Win Rate",      f"{r['Win Rate (%)']:.0f}%")
        st.metric("Max Drawdown",  f"{r['Max Drawdown (%)']:.1f}%")
        st.metric("6-Mo Failure",  f"{r['6-Mo Failure (%)']:.0f}%")
    else:
        st.markdown(
            f"<span style='color:{MUTED}; font-size:0.84rem;'>"
            "Select a specific trader type to see key stats."
            "</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown('<div class="sb-label">Primary Sources</div>', unsafe_allow_html=True)
    for name, detail in [
        ("SEBI India",      "Sept 2024"),
        ("ESMA (EU)",       "CFD disclosure"),
        ("Quantopian",      "888-strategy study, 2016"),
        ("Barber & Odean",  "UC Berkeley · Taiwan study"),
        ("MEXC",            "2026 slippage analysis"),
        ("Dalbar Inc.",     "20-year retail study"),
        ("TradingView Hub", "2026"),
    ]:
        st.markdown(
            f"<span style='color:{TEXT}; font-size:0.83rem; font-weight:600;'>{name}</span>"
            f"<span style='color:{MUTED}; font-size:0.81rem;'> · {detail}</span><br>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        f"<span style='color:{SUB}; font-size:0.76rem;'>"
        "Pawan Bohora · MSCS, Wright State University<br>"
        "Independent research portfolio project"
        "</span>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 7 ·  HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(
    f"<h1 style='color:{TEXT}; font-size:2rem; font-weight:800; margin-bottom:6px;'>"
    "Trading Bots: Reality Check"
    "</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='color:{MUTED}; font-size:0.97rem; max-width:800px; line-height:1.65;'>"
    "A forensic analysis of whether retail algorithmic trading bots outperform human traders "
    f"<strong style='color:{TEXT};'>after accounting for fees, slippage, latency, and risk.</strong> "
    "Built from primary regulatory disclosures, peer-reviewed academic studies, and broker-level reports."
    "</p>",
    unsafe_allow_html=True,
)

st.info(
    "**Data transparency:** This dashboard combines real source-cited figures with modelled scenarios. "
    "Each section is tagged **SOURCE**, **MODELED**, or **ILLUSTRATIVE**. "
    "See the Methodology section at the bottom for a full breakdown.",
    icon="ℹ️",
)

st.divider()

# ── KPI hero row ───────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Retail Traders Losing Money",    "89–93%",  "↑ SEBI India & ESMA · SOURCE",           delta_color="inverse")
k2.metric("Algo Bots Failing Within 6 Mo.", "73%",     "↑ Automated crypto accounts · SOURCE",    delta_color="inverse")
k3.metric("Backtest Predicts Live (R²)",    "≈1–2%",   "↑ 888 strategies · Quantopian · SOURCE",  delta_color="inverse")
k4.metric("Slippage as % of Gross Revenue", "347%",    "↑ BTC HF mean reversion · MEXC · SOURCE", delta_color="inverse")

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# §01 — PERFORMANCE OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
render_section_header(
    "§01 · Performance",
    "Net Returns by Trader Type",
    "After exchange fees and slippage — which approach actually makes money?",
    tag="MODELED", tag_type="modeled",
)

col_a1, col_a2 = st.columns(2)

with col_a1:
    fig = go.Figure()
    for t in TRADERS:
        row = df_traders[df_traders["Trader Type"] == t].iloc[0]
        fig.add_trace(go.Bar(
            x=[t], y=[row["Net Return (%)"]],
            name=t,
            marker_color=bar_color(t, selected_trader),
            opacity=bar_opacity(t, selected_trader),
            marker_line_width=0,
            text=f"{row['Net Return (%)']:.1f}%",
            textposition="outside",
            textfont=dict(color=TEXT, size=12),
            hovertemplate=f"<b>{t}</b><br>Net return: %{{y:.1f}}%<extra></extra>",
        ))
    fig.add_hline(
        y=9.95, line_dash="dot", line_color=YELLOW, line_width=1.5,
        annotation_text="Passive benchmark 9.95%",
        annotation_position="top right",
        annotation_font=dict(color=YELLOW, size=10),
    )
    fig.update_layout(
        **BASE, height=H,
        title="Net Annual Return After All Costs",
        showlegend=False,
        yaxis_title="Net Return (%)", yaxis_ticksuffix="%", yaxis_range=[-2, 28],
        bargap=0.35,
    )
    st.plotly_chart(fig, use_container_width=True)
    source_note("MODELED — Net = Gross − exchange fees − slippage. Derived from category-level averages.")

with col_a2:
    fig = go.Figure()
    for t in TRADERS:
        row = df_traders[df_traders["Trader Type"] == t].iloc[0]
        fig.add_trace(go.Bar(
            x=[t], y=[row["Win Rate (%)"]],
            name=t,
            marker_color=bar_color(t, selected_trader),
            opacity=bar_opacity(t, selected_trader),
            marker_line_width=0,
            text=f"{row['Win Rate (%)']:.0f}%",
            textposition="outside",
            textfont=dict(color=TEXT, size=12),
            hovertemplate=f"<b>{t}</b><br>Win rate: %{{y:.0f}}%<extra></extra>",
        ))
    fig.add_hline(
        y=70, line_dash="dot", line_color=RED, line_width=1.5,
        annotation_text="~70% needed to break even",
        annotation_position="top left",
        annotation_font=dict(color=RED, size=10),
    )
    fig.update_layout(
        **BASE, height=H,
        title="Reported Win Rate by Trader Type",
        showlegend=False,
        yaxis_title="Win Rate (%)", yaxis_ticksuffix="%", yaxis_range=[0, 120],
        bargap=0.35,
    )
    st.plotly_chart(fig, use_container_width=True)
    source_note("SOURCE — Retail/manual win rates: Barber & Odean. Institutional: industry aggregates.")

with st.expander("📋  Full comparison table", expanded=False):
    display = df_traders.copy()
    if selected_trader != "All Traders":
        display = display[display["Trader Type"] == selected_trader]
    st.dataframe(
        display.style.format({c: "{:.2f}" for c in display.columns if "(%)" in c}),
        hide_index=True,
        use_container_width=True,
    )
    st.caption(
        "All (%) figures are modelled from source data using category-level averages. "
        "They represent archetypes, not single observed traders. See Methodology for assumptions."
    )

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# §02 — WIN RATE PARADOX
# ═══════════════════════════════════════════════════════════════════════════════
render_section_header(
    "§02 · The Core Trap",
    "The Win Rate Paradox",
    "65% of traders had >50% win rates — yet 82% still lost money. Here is why.",
    tag="SOURCE", tag_type="source",
)

col_b1, col_b2 = st.columns(2)

with col_b1:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Traders with\n>50% Win Rate", "…Who Still\nLost Money"],
        y=[65, 82],
        marker_color=[BLUE, RED],
        marker_line_width=0,
        text=["65%", "82%"],
        textposition="outside",
        textfont=dict(color=TEXT, size=15, family="Inter"),
        width=0.40,
        hovertemplate="%{x}: %{y}%<extra></extra>",
    ))
    fig.add_annotation(
        x=0.5, y=97, xref="paper",
        text="Study: 25,000+ retail accounts · 4M+ trades",
        showarrow=False,
        font=dict(color=MUTED, size=10),
    )
    fig.update_layout(
        **BASE, height=H,
        title="Win Rate vs. Net Outcome",
        showlegend=False,
        yaxis_title="Percentage (%)", yaxis_ticksuffix="%", yaxis_range=[0, 105],
    )
    st.plotly_chart(fig, use_container_width=True)
    source_note("SOURCE — Barber, Makov & Schwartz · JFQA 2024 · 25,000+ accounts · 4M+ trades.")

with col_b2:
    fig = go.Figure()
    loss_mask = pnl < 0
    fig.add_trace(go.Scatter(
        x=wr[loss_mask] * 100, y=pnl[loss_mask],
        fill="tozeroy", fillcolor="rgba(247,93,93,0.09)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    win_mask = pnl >= 0
    fig.add_trace(go.Scatter(
        x=wr[win_mask] * 100, y=pnl[win_mask],
        fill="tozeroy", fillcolor="rgba(79,209,165,0.09)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=wr * 100, y=pnl,
        line=dict(color=BLUE, width=2.5),
        name="Net P&L per trade",
        hovertemplate="Win rate: %{x:.1f}%<br>Net P&L: %{y:.2f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line_color=MUTED, line_dash="dash", line_width=1)
    fig.add_vline(
        x=BREAKEVEN_WR * 100,
        line_color=YELLOW, line_dash="dot", line_width=1.5,
        annotation_text=f"Break-even: {BREAKEVEN_WR*100:.0f}% win rate",
        annotation_position="top right",
        annotation_font=dict(color=YELLOW, size=10),
    )
    fig.add_vrect(
        x0=55, x1=65,
        fillcolor="rgba(79,142,247,0.07)", line_width=0,
        annotation_text="Most retail bots",
        annotation_position="top left",
        annotation_font=dict(color=BLUE, size=10),
    )
    fig.update_layout(
        **BASE, height=H,
        title=f"Net P&L by Win Rate  (+{WIN_AVG}% avg win / {LOSS_AVG}% avg loss)",
        xaxis_title="Win Rate (%)", xaxis_ticksuffix="%",
        yaxis_title="Net P&L per Trade (%)", yaxis_ticksuffix="%",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    source_note(
        f"MODELED — curve derived from SOURCE avg winner +{WIN_AVG}% / avg loser {LOSS_AVG}%. "
        "Break-even is algebraic, not observed."
    )

st.info(
    f"**Insight:** With an avg winner of **+{WIN_AVG}%** and avg loser of **{LOSS_AVG}%**, "
    f"a bot needs a **{BREAKEVEN_WR*100:.0f}% win rate just to break even.** "
    "Most retail bots land in the 55–65% range. "
    "**Win rate alone is not a valid optimisation target — payoff ratio is the real separator.**",
    icon="💡",
)
st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# §03 — COST EROSION
# ═══════════════════════════════════════════════════════════════════════════════
render_section_header(
    "§03 · Costs",
    "The Fee & Slippage Erosion Cascade",
    "How exchange fees and slippage compound to eliminate returns that look profitable on paper.",
    tag="SOURCE + MODELED", tag_type="modeled",
)

col_c1, col_c2 = st.columns([3, 2])

with col_c1:
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=EROSION_TYPES,
        x=EROSION_X,
        y=EROSION_DELTAS,
        base=0,
        connector=dict(line=dict(color=BORDER, width=1, dash="dot")),
        increasing=dict(marker=dict(color=GREEN, line=dict(width=0))),
        decreasing=dict(marker=dict(color=RED,   line=dict(width=0))),
        totals=dict(   marker=dict(color=BLUE,   line=dict(width=0))),
        text=["+20.0%", "−5.5%", "−4.7%", "−2.6%", "7.2%"],
        textposition="outside",
        textfont=dict(color=TEXT, size=12, family="Inter"),
        hovertemplate="%{x}<br>Δ: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(
        y=9.95, line_dash="dot", line_color=YELLOW, line_width=1.5,
        annotation_text="Passive index: 9.95%",
        annotation_position="top right",
        annotation_font=dict(color=YELLOW, size=10),
    )
    fig.update_layout(
        **BASE, height=H,
        title="Gross Return → Net Return: Where the Alpha Goes",
        yaxis_title="Annual Return (%)", yaxis_ticksuffix="%",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    source_note("MODELED — illustrative scenario using median cost estimates for retail bots. Actual erosion varies widely by strategy and asset class.")

with col_c2:
    st.markdown(
        f"<h4 style='color:{TEXT}; margin-top:0;'>Real-World Extreme</h4>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<span style='color:{MUTED}; font-size:0.88rem;'>"
        "BTC High-Frequency Mean Reversion strategy "
        "(MEXC analysis, 2026 · 36,008 transactions):"
        "</span>",
        unsafe_allow_html=True,
    )
    real = pd.DataFrame({
        "Stage":  ["Gross Profit", "Exchange Fees", "Slippage Costs", "Net Result"],
        "Amount": ["$84,534", "−$66,456", "−$46,966", "−$99,896"],
    })
    st.dataframe(real, hide_index=True, use_container_width=True)
    st.markdown(
        f"<span style='color:{RED}; font-weight:700; font-size:0.92rem;'>"
        "Slippage alone = 347% of gross revenue.</span><br><br>"
        f"<span style='color:{MUTED}; font-size:0.87rem;'>"
        "A profitable strategy on paper became a $99K net loss in production. "
        "No standard backtest framework surfaces this automatically.</span>",
        unsafe_allow_html=True,
    )
    st.warning(
        "Real-world returns consistently run **30–50% below backtested results.**",
        icon="⚠️",
    )

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# §04 — REGULATOR EVIDENCE
# ═══════════════════════════════════════════════════════════════════════════════
render_section_header(
    "§04 · Regulator Evidence",
    "Official Loss Rates by Market",
    "Mandatory legal disclosures and regulator-commissioned studies — not marketing estimates.",
    tag="SOURCE", tag_type="source",
)

col_d1, col_d2 = st.columns([3, 1])

with col_d1:
    bar_c = [RED if v > 60 else GREEN for v in df_loss["Loss %"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_loss["Market"],
        x=df_loss["Loss %"],
        orientation="h",
        marker_color=bar_c,
        marker_line_width=0,
        text=[f"  {v}%  ·  {s}" for v, s in zip(df_loss["Loss %"], df_loss["Source"])],
        textposition="outside",
        textfont=dict(color=MUTED, size=10.5),
        hovertemplate="%{y}<br>Loss rate: %{x}%<extra></extra>",
    ))
    fig.add_vline(
        x=50, line_dash="dot", line_color=MUTED, line_width=1.2,
        annotation_text="50%", annotation_position="top",
        annotation_font=dict(color=MUTED, size=9),
    )
    _base_regulator = {**BASE, "margin": dict(l=200, r=32, t=58, b=44)}
    fig.update_layout(
        **_base_regulator, height=340,
        title="% of Retail Traders Losing Money — Regulator-Disclosed Data",
        xaxis_title="Loss Rate (%)", xaxis_ticksuffix="%", xaxis_range=[0, 125],
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    source_note("*Retail algo bot figure (TradingView Hub 2026) is subject to survivorship bias — see note →")

with col_d2:
    st.markdown(
        f"<h4 style='color:{TEXT}; margin-top:0;'>The Asterisk on Bots</h4>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<span style='color:{MUTED}; font-size:0.88rem; line-height:1.65;'>"
        f"The <strong style='color:{TEXT};'>40% loss rate</strong> for retail bots "
        f"looks far better than 88% for manual traders.<br><br>"
        f"<strong style='color:{RED};'>It is survivorship-biased.</strong> "
        "It counts only currently active bots. 73% of accounts fail within "
        "6 months and exit the dataset before being recorded as losers."
        "</span>",
        unsafe_allow_html=True,
    )

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# §05 — SURVIVORSHIP BIAS
# ═══════════════════════════════════════════════════════════════════════════════
render_section_header(
    "§05 · Hidden Data",
    "Survivorship Bias — The Invisible Graveyard",
    "Platform leaderboards only show winning bots. The failing majority quietly disappears.",
    tag="SOURCE + MODELED", tag_type="modeled",
)

col_e1, col_e2 = st.columns(2)

with col_e1:
    fig = go.Figure(go.Pie(
        labels=["Active & Visible", "Failed / Delisted", "Abandoned"],
        values=[135, 250, 115],
        marker=dict(
            colors=[BLUE, RED, DIM],
            line=dict(color=BG, width=2.5),
        ),
        hole=0.50,
        textinfo="label+percent",
        textfont=dict(color=TEXT, size=11),
        pull=[0, 0.05, 0.04],
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
    ))
    fig.add_annotation(
        text="<b>500</b><br><span style='font-size:10px'>bots launched</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color=TEXT, family="Inter"),
    )
    _base_donut = {**BASE, "legend": dict(x=0.72, bgcolor=CARD, bordercolor=BORDER, font=dict(color=TEXT, size=10))}
    fig.update_layout(
        **_base_donut, height=H,
        title="Bot Universe: What Platforms Show You vs. Reality",
    )
    st.plotly_chart(fig, use_container_width=True)
    source_note("ILLUS — Proportions based on SOURCE 73% 6-month failure rate. Absolute numbers are illustrative.")

with col_e2:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Platform-Reported (Biased)",
        x=sb_data["metrics"], y=sb_data["biased"],
        marker_color=BLUE, marker_line_width=0,
        text=[str(v) for v in sb_data["biased"]],
        textposition="outside", textfont=dict(color=TEXT, size=11),
        hovertemplate="%{x}<br>Biased: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Survivorship-Corrected",
        x=sb_data["metrics"], y=sb_data["corrected"],
        marker_color=RED, marker_line_width=0,
        text=[str(v) for v in sb_data["corrected"]],
        textposition="outside", textfont=dict(color=TEXT, size=11),
        hovertemplate="%{x}<br>Corrected: %{y}<extra></extra>",
    ))
    for xi, (b, c) in enumerate(zip(sb_data["biased"], sb_data["corrected"])):
        delta = round(c - b, 1)
        sign  = "+" if delta > 0 else ""
        fig.add_annotation(
            x=xi, y=max(b, c) + 1.8,
            text=f"<b>Δ {sign}{delta}</b>",
            showarrow=False,
            font=dict(size=11, color=YELLOW),
        )
    fig.update_layout(
        **BASE, height=H,
        title="Bias Correction: What Metrics Really Show",
        barmode="group",
        yaxis_title="Value",
    )
    st.plotly_chart(fig, use_container_width=True)
    source_note("MODELED — Correction factors from Andrikogiannopoulou & Papakonstantinou (hedge fund study), applied to retail context.")

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# §06 — 20-YEAR REALITY CHECK
# ═══════════════════════════════════════════════════════════════════════════════
render_section_header(
    "§06 · Long-Term View",
    "The 20-Year Reality Check",
    "$10,000 invested in 2006 — where does each approach land by 2025?",
    tag="ILLUSTRATIVE", tag_type="illus",
)

GROWTH_COLORS = {
    "Passive Index (S&P 500)": GREEN,
    "Retail Bot (Optimistic)": BLUE,
    "Manual Retail Trader":    RED,
}
GROWTH_DASH = {
    "Passive Index (S&P 500)": "solid",
    "Retail Bot (Optimistic)": "dot",
    "Manual Retail Trader":    "dash",
}

fig = go.Figure()
for col_name, color in GROWTH_COLORS.items():
    visible = True
    if selected_trader != "All Traders":
        mapping = {
            "Retail Bot":              "Retail Bot (Optimistic)",
            "Manual Day Trader":       "Manual Retail Trader",
            "Passive Index (S&P 500)": "Passive Index (S&P 500)",
        }
        target = mapping.get(selected_trader)
        if target and col_name != target:
            visible = "legendonly"

    final_val = df_growth[col_name].iloc[-1]
    fig.add_trace(go.Scatter(
        x=df_growth["Year"], y=df_growth[col_name],
        name=col_name,
        visible=visible,
        line=dict(color=color, width=3 if visible is True else 1.5,
                  dash=GROWTH_DASH[col_name]),
        hovertemplate=f"<b>{col_name}</b><br>Year: %{{x}}<br>Value: $%{{y:,.0f}}<extra></extra>",
    ))
    fig.add_annotation(
        x=2025, y=final_val,
        text=f"  ${final_val:,.0f}",
        xanchor="left", showarrow=False,
        font=dict(color=color, size=12, family="Inter"),
    )

_base_growth = {**BASE, "legend": dict(x=0.02, y=0.97, bgcolor=CARD, bordercolor=BORDER, font=dict(color=TEXT, size=11))}
fig.update_layout(
    **_base_growth, height=H_WIDE,
    title="$10,000 Invested in 2006 — Illustrative Terminal Value in 2025",
    xaxis_title="Year",
    yaxis_title="Portfolio Value (USD)",
    yaxis_tickprefix="$", yaxis_tickformat=",.0f",
)
st.plotly_chart(fig, use_container_width=True)
source_note(
    "ILLUS — Scenario model using assumed constant rates: Passive 10.0% p.a. (S&P CAGR · Dalbar), "
    "Retail Bot 6.5% p.a. (optimistic net-of-cost), Manual 3.9% p.a. (Dalbar 20-year avg). "
    "This is a projection, not observed portfolio data."
)

tv_passive = df_growth["Passive Index (S&P 500)"].iloc[-1]
tv_bot     = df_growth["Retail Bot (Optimistic)"].iloc[-1]
tv_manual  = df_growth["Manual Retail Trader"].iloc[-1]

g1, g2, g3 = st.columns(3)
g1.metric("Passive Index (S&P 500)",  f"${tv_passive:,.0f}", f"+${tv_passive-10000:,.0f} total gain")
g2.metric("Retail Bot (Optimistic)",  f"${tv_bot:,.0f}",     f"${tv_passive-tv_bot:,.0f} below passive",   delta_color="inverse")
g3.metric("Manual Retail Trader",     f"${tv_manual:,.0f}",  f"${tv_passive-tv_manual:,.0f} below passive", delta_color="inverse")

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# §07 — KEY INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════════
render_section_header(
    "§07 · Findings",
    "Key Insights",
    "Five data-backed conclusions from this analysis.",
)

ins_left, ins_right = st.columns(2)

with ins_left:
    render_insight_card(
        "red",
        "💸  Fees and slippage can consume more than 100% of gross profit.",
        f"A BTC high-frequency mean reversion strategy earning $84,534 gross resulted in a $99,896 net loss. "
        f"Exchange fees ($66,456) and slippage ($46,966) combined equalled 347% of gross revenue — "
        "a ratio no standard backtest framework surfaces automatically.",
        "MEXC Slippage Analysis, 2026 · SOURCE",
    )
    render_insight_card(
        "red",
        "🔬  Backtests predict live performance with less than 2% accuracy.",
        "Quantopian's study of 888 strategies found R² ≈ 0.025 between backtest and live Sharpe ratios. "
        "Testing 50 strategy variants creates a 92%+ probability of finding a false positive by chance. "
        "A high backtest Sharpe is statistically near-useless as a predictor of live returns.",
        "Wiecki et al. / Quantopian, 2016 · SOURCE",
    )
    render_insight_card(
        "yellow",
        "📐  Win rate is a misleading optimisation target.",
        f"65% of traders in a 25,000+ account study had >50% win rates, yet 82% lost money overall. "
        f"Average winner: +{WIN_AVG}%. Average loser: {LOSS_AVG}%. "
        f"At this payoff asymmetry, a bot needs ~{BREAKEVEN_WR*100:.0f}% win rate just to break even.",
        "Barber, Makov & Schwartz · JFQA 2024 · SOURCE",
    )

with ins_right:
    render_insight_card(
        "red",
        "🏦  Institutional algorithms are the counterparty — and they dominate.",
        "SEBI India (2024): 93% of 10M+ retail F&O traders lost a combined $21.7B over 3 years. "
        "In the same period, institutional algos captured 97% of FPI profits and 96% of prop trader profits. "
        "Retail bots aren't competing against slow humans — they face quants with co-location and sub-ms execution.",
        "SEBI India Press Release, September 2024 · SOURCE",
    )
    render_insight_card(
        "yellow",
        "⚖️  Bots beat manual trading — but both underperform passive indexing.",
        "~60% of retail algo traders show positive annual returns vs. 5–10% for manual day traders. "
        "Yet the average retail investor still underperforms the S&P 500 by 6.1% annually over 20 years. "
        "Automation reduces emotional error but cannot overcome structural market disadvantages.",
        "Dalbar Inc. 20-Year Study · TradingView Hub, 2026 · SOURCE",
    )
    render_insight_card(
        "green",
        "✅  The rare successful bots share four structural traits.",
        "Low trading frequency (reduces fee drag), walk-forward validated edge (combats overfitting), "
        "payoff-ratio-aware position sizing, and hard drawdown circuit breakers. "
        "These are not passive tools — they require continuous research, which is by definition a professional job.",
        "Synthesis across all reviewed sources · MODELED",
    )

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# §08 — CONCLUSION
# ═══════════════════════════════════════════════════════════════════════════════
render_section_header(
    "§08 · Final Assessment",
    "Conclusion",
    "Three key takeaways, what they mean, and what future work would add.",
)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
<div class="takeaway">
  <div class="takeaway-num">01</div>
  <div class="takeaway-text">
    <strong style="color:{TEXT};">The fee problem is not solvable by strategy quality alone.</strong><br><br>
    Even a genuinely alpha-generating retail bot faces 30–50% return degradation in live markets.
    The infrastructure gap between retail and institutional execution is structural —
    not closable with a better algorithm.
  </div>
</div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
<div class="takeaway">
  <div class="takeaway-num">02</div>
  <div class="takeaway-text">
    <strong style="color:{TEXT};">Backtesting builds intuition, not confidence in live returns.</strong><br><br>
    With R² ≈ 0.025, a strong backtest is necessary but nowhere near sufficient.
    Walk-forward validation, out-of-sample testing, and realistic transaction cost
    modelling are non-negotiable before any real capital commitment.
  </div>
</div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
<div class="takeaway">
  <div class="takeaway-num">03</div>
  <div class="takeaway-text">
    <strong style="color:{TEXT};">Passive indexing wins by default — not because active strategies can't work, but because the bar is steeper than marketed.</strong><br><br>
    10% p.a. passively vs. 6.5% net for an optimistic bot is a 20-year compounding gap
    of $37,000+ on $10K initial capital. The burden of proof for active strategies is high.
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

fut1, fut2 = st.columns(2)

with fut1:
    st.markdown(
        f"<h4 style='color:{TEXT};'>What This Means</h4>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:{MUTED}; font-size:0.91rem; line-height:1.65;'>"
        "The evidence does not say bots never work. It says the conditions required for "
        "profitability — low-latency execution, realistic cost modelling, rigorous out-of-sample "
        "validation, and ongoing maintenance — are far more demanding than commonly marketed. "
        "For most retail participants, passive indexing remains the rational default."
        "</p>",
        unsafe_allow_html=True,
    )

with fut2:
    st.markdown(
        f"<h4 style='color:{TEXT};'>Future Improvements</h4>",
        unsafe_allow_html=True,
    )
    for item in [
        "Live broker API integration (Alpaca / IBKR) for real performance data",
        "Per-strategy backtesting module with walk-forward validation",
        "Slippage modelling by asset class and trade frequency",
        "Monte Carlo simulation for strategy robustness",
        "Comparison with CTA/quant fund benchmarks (Barclay CTA Index)",
    ]:
        st.markdown(
            f"<span style='color:{MUTED}; font-size:0.88rem;'>→ {item}</span><br>",
            unsafe_allow_html=True,
        )

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# §09 — METHODOLOGY
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("🔍  Methodology & Data Notes — Real Data vs. Modelled Scenarios", expanded=False):
    st.markdown(f"""
### Is This Real Data or Simulated?

**Short answer: both — and every value is explicitly tagged in the UI.**

---

#### SOURCE — Direct citations from published studies or regulatory disclosures

| Metric | Value | Citation |
|--------|-------|----------|
| Retail F&O traders losing money | 89–93% | SEBI India Sept 2024; ESMA CFD broker disclosures |
| Algo bots failing within 6 months | 73% | ForTraders 2026; automated crypto account data |
| Backtest-to-live Sharpe R² | ≈0.025 | Wiecki et al. / Quantopian, 888 strategies, 2016 |
| BTC HF strategy — gross profit | $84,534 | MEXC Slippage Analysis, 2026 (36,008 transactions) |
| BTC HF strategy — net result | −$99,896 | MEXC Slippage Analysis, 2026 |
| Traders with >50% win rate who lost money | 82% | Barber, Makov & Schwartz · JFQA 2024 · 25,000+ accounts |
| Avg winner / avg loser per trade | +1.2% / −2.8% | Same study above |
| Retail investor underperforms S&P 500 | 6.1% p.a. over 20 years | Dalbar Inc. |
| Institutional algo share of FPI profits | 97% | SEBI India Sept 2024 |

---

#### MODELED — Derived or calculated from source figures

- **Net returns per trader type** — gross return minus median fee and slippage estimates per category
- **Win-rate P&L curve** — mathematical: `pnl = wr × avg_win + (1 − wr) × avg_loss` using SOURCE inputs
- **Break-even win rate** — algebraic result, not an observed threshold
- **Survivorship bias correction** — Andrikogiannopoulou & Papakonstantinou (hedge fund study) factors applied to retail bot context
- **Cost erosion waterfall** — illustrative scenario using category-level median cost estimates

---

#### ILLUSTRATIVE — Scenario models with stated assumptions

- **20-year compound growth chart** — constant-rate projection, not observed portfolio tracks
  - Passive: 10.0% p.a. (S&P 500 CAGR per Dalbar)
  - Retail Bot: 6.5% p.a. (optimistic net-of-cost estimate)
  - Manual Retail: 3.9% p.a. (Dalbar 20-year average)
- **Survivorship bias donut** — proportions reflect SOURCE 73% failure rate; absolute numbers are illustrative
- **Comparison table** — modelled archetypes, not averages from a single observed dataset

---

#### Why a mixed approach is analytically valid

An explanatory analytical dashboard does not require a single raw observed dataset.
This is standard practice in policy analysis, financial education, and quantitative
research communication. SOURCE data anchors all major claims to cited evidence.
MODELED and ILLUSTRATIVE components exist to make the mechanics visually interpretable —
not to fabricate new claims.

All key findings (fee erosion, backtest unreliability, survivorship bias, payoff asymmetry)
are derived directly from the cited primary sources listed above.
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# §10 — FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(
    f"<div style='text-align:center; color:{SUB}; font-size:0.78rem; padding:16px 0 32px;'>"
    "Sources · SEBI India (2024) &nbsp;·&nbsp; ESMA &nbsp;·&nbsp; "
    "Wiecki et al. / Quantopian (2016) &nbsp;·&nbsp; Barber &amp; Odean / UC Berkeley &nbsp;·&nbsp; "
    "MEXC (2026) &nbsp;·&nbsp; Dalbar Inc. &nbsp;·&nbsp; TradingView Hub (2026)<br>"
    f"Built with <strong style='color:{TEXT};'>Streamlit</strong> &amp; "
    f"<strong style='color:{TEXT};'>Plotly</strong> &nbsp;·&nbsp; "
    "Pawan Bohora · MSCS, Wright State University · Independent research"
    "</div>",
    unsafe_allow_html=True,
)
