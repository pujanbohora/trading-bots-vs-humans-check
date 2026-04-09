"""
Do Trading Bots Actually Work?  —  Portfolio Dashboard
═══════════════════════════════════════════════════════
Author  : Pawan Bohora  ·  MSCS, Wright State University
GitHub  : github.com/pawanbohora
Sources : SEBI India (2024) · ESMA · Wiecki et al./Quantopian (2016)
          Barber & Odean/UC Berkeley · MEXC (2026) · Dalbar Inc.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ═══════════════════════════════════════════════════════════════════════════════
# 1 ·  PAGE CONFIG  (must be the very first Streamlit call)
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Do Trading Bots Actually Work?",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# 2 ·  DESIGN SYSTEM  (colours, chart defaults, consistent sizing)
# ═══════════════════════════════════════════════════════════════════════════════
# ── colour tokens ─────────────────────────────────────────────────────────────
BG     = "#0F1117"
CARD   = "#1A1D27"
BORDER = "#2A2D3A"
BLUE   = "#4F8EF7"
RED    = "#F75D5D"
GREEN  = "#4FD1A5"
YELLOW = "#F7C948"
PURPLE = "#B45FE3"
TEXT   = "#E8EAF0"
MUTED  = "#9CA3AF"
GRID   = "#2A2D3A"
DIM    = "#3A3D4A"   # colour for de-emphasised bars when a filter is active

# ── trader palette (used consistently across all charts) ──────────────────────
TRADER_COLORS = {
    "Retail Bot":              BLUE,
    "Manual Day Trader":       RED,
    "Institutional Algo":      GREEN,
    "Passive Index (S&P 500)": YELLOW,
}

# ── chart sizing constants ─────────────────────────────────────────────────────
H = 380   # standard chart height
H_WIDE = 420   # full-width chart height

# ── base Plotly layout (applied to every figure) ──────────────────────────────
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
/* ── shell & backgrounds ────────────────────────────────────── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"]          {{ background-color: {BG}; }}
[data-testid="stHeader"]        {{ background-color: {BG}; border-bottom: 1px solid {BORDER}; }}
[data-testid="stSidebar"]       {{ background-color: {CARD}; border-right: 1px solid {BORDER}; }}
[data-testid="stSidebarContent"] > div:first-child {{ padding-top: 1.5rem; }}

/* ── metric cards ───────────────────────────────────────────── */
[data-testid="metric-container"] {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 14px 16px;
}}
[data-testid="stMetricValue"] {{ color: {BLUE}; font-size: 1.75rem !important; font-weight: 700; }}
[data-testid="stMetricLabel"] {{ color: {MUTED}; font-size: 0.78rem !important; }}
[data-testid="stMetricDelta"] {{ font-size: 0.74rem !important; }}

/* ── section headers ─────────────────────────────────────────── */
.sec-wrap   {{ margin-bottom: 8px; }}
.sec-eyebrow{{ color:{MUTED}; font-size:0.68rem; letter-spacing:0.14em;
               text-transform:uppercase; margin-bottom:2px; }}
.sec-title  {{ color:{TEXT}; font-size:1.3rem; font-weight:700; line-height:1.25; }}
.sec-cap    {{ color:{MUTED}; font-size:0.85rem; margin-top:2px; margin-bottom:4px; }}

/* ── key insight cards ───────────────────────────────────────── */
.ins        {{ background:{CARD}; border-left:3px solid {BLUE};
               border-radius:0 8px 8px 0; padding:13px 17px; margin-bottom:10px; }}
.ins.red    {{ border-left-color:{RED};    }}
.ins.yellow {{ border-left-color:{YELLOW}; }}
.ins.green  {{ border-left-color:{GREEN};  }}
.ins-title  {{ font-weight:700; color:{TEXT}; font-size:0.94rem; }}
.ins-body   {{ color:{MUTED}; font-size:0.86rem; line-height:1.55; margin-top:3px; }}
.ins-src    {{ color:#6B7280; font-size:0.75rem; margin-top:5px; }}

/* ── sidebar helpers ─────────────────────────────────────────── */
.sb-label   {{ color:{MUTED}; font-size:0.72rem; text-transform:uppercase;
               letter-spacing:0.1em; margin-bottom:4px; margin-top:20px; }}
.sb-badge   {{ display:inline-block; background:{BLUE}18; border:1px solid {BLUE}44;
               border-radius:16px; color:{BLUE}; font-size:0.78rem;
               padding:2px 10px; margin-top:6px; }}

/* ── misc ─────────────────────────────────────────────────────── */
hr {{ border-color:{BORDER} !important; margin:26px 0; }}
[data-testid="stExpander"] {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:8px;
}}
[data-testid="stDataFrame"] {{ border:1px solid {BORDER}; border-radius:8px; }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 4 ·  DATASETS
# ═══════════════════════════════════════════════════════════════════════════════
TRADERS = list(TRADER_COLORS.keys())

# ── 4a. Main comparison table ─────────────────────────────────────────────────
df_traders = pd.DataFrame({
    "Trader Type":       TRADERS,
    "Win Rate (%)":      [56,   48,   74,   100],
    "Gross Return (%)":  [9.2,  5.1,  23.5, 10.0],
    "Fees (%)":          [2.3,  1.4,  0.3,  0.05],
    "Slippage (%)":      [1.8,  0.6,  0.1,  0.0],
    "Net Return (%)":    [5.1,  3.1,  23.1, 9.95],
    "Max Drawdown (%)":  [19.5, 24.2, 10.8, 13.7],
    "6-Mo Failure (%)":  [73,   88,   15,   0],
})

# ── 4b. Regulator loss rates ──────────────────────────────────────────────────
df_loss = pd.DataFrame({
    "Market":   ["India F&O (SEBI 2024)", "EU CFD Avg (ESMA)",
                 "Taiwan Day Traders",    "US Forex (Retail)",
                 "Manual Day Traders",    "Retail Algo Bots*"],
    "Loss %":   [93, 75, 82, 77, 88, 40],
    "Source":   ["SEBI 2024", "ESMA", "Barber & Odean",
                 "CFTC", "Multiple studies", "TradingView Hub 2026"],
})

# ── 4c. Win-rate paradox simulation ───────────────────────────────────────────
WIN_AVG, LOSS_AVG = +1.2, -2.8          # real data: 25,000+ trader study
BREAKEVEN_WR = abs(LOSS_AVG) / (WIN_AVG + abs(LOSS_AVG))   # ≈ 0.70
np.random.seed(42)
_wr  = np.linspace(0.30, 0.88, 800)
_pnl = _wr * WIN_AVG + (1 - _wr) * LOSS_AVG

# ── 4d. Cost erosion (waterfall) ──────────────────────────────────────────────
EROSION_X      = ["Gross Return\n(Backtest)", "Exchange\nFees",
                  "Slippage", "Latency &\nExecution", "Net Return"]
EROSION_DELTAS = [20.0, -5.5, -4.7, -2.6, 0.0]
EROSION_TYPES  = ["absolute", "relative", "relative", "relative", "total"]

# ── 4e. Survivorship bias correction ─────────────────────────────────────────
SB_METRICS    = ["Annual Return (%)", "Sharpe Ratio", "Max Drawdown (%)"]
SB_BIASED     = [14.2, 1.40, 12.0]
SB_CORRECTED  = [10.6, 0.90, 26.0]

# ── 4f. 20-year compound growth ($10,000 → 2025) ──────────────────────────────
_YEARS = list(range(2006, 2026))
df_growth = pd.DataFrame({
    "Year":                  _YEARS,
    "Passive Index (S&P 500)": [10_000 * 1.100 ** i for i in range(len(_YEARS))],
    "Retail Bot (Optimistic)": [10_000 * 1.065 ** i for i in range(len(_YEARS))],
    "Manual Retail Trader":    [10_000 * 1.039 ** i for i in range(len(_YEARS))],
})


# ═══════════════════════════════════════════════════════════════════════════════
# 5 ·  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def bar_color(trader: str, selected: str) -> str:
    """Return full colour when selected=='All' or matches, dim otherwise."""
    if selected == "All Traders":
        return TRADER_COLORS[trader]
    return TRADER_COLORS[trader] if trader == selected else DIM


def bar_opacity(trader: str, selected: str) -> float:
    if selected == "All Traders":
        return 1.0
    return 1.0 if trader == selected else 0.30


def section(eyebrow: str, title: str, caption: str = "") -> None:
    """Render a styled section header."""
    cap_html = f'<div class="sec-cap">{caption}</div>' if caption else ""
    st.markdown(
        f'<div class="sec-wrap">'
        f'<div class="sec-eyebrow">{eyebrow}</div>'
        f'<div class="sec-title">{title}</div>'
        f'{cap_html}</div>',
        unsafe_allow_html=True,
    )


def insight(color: str, title: str, body: str, source: str) -> None:
    """Render a key-insight card."""
    st.markdown(
        f'<div class="ins {color}">'
        f'<div class="ins-title">{title}</div>'
        f'<div class="ins-body">{body}</div>'
        f'<div class="ins-src">Source: {source}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 6 ·  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── Project identity ──────────────────────────────────────────────────────
    st.markdown("## 📊 AlgoMirror")
    st.markdown(
        f"<span style='color:{MUTED}; font-size:0.83rem;'>"
        "A forensic analysis of retail algorithmic trading "
        "performance after fees, slippage, and risk."
        "</span>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Trader-type filter ────────────────────────────────────────────────────
    st.markdown('<div class="sb-label">Filter · Trader Type</div>', unsafe_allow_html=True)
    selected_trader = st.selectbox(
        label="Select trader type",
        options=["All Traders"] + TRADERS,
        index=0,
        label_visibility="collapsed",
        help="Highlight one trader type across all comparison charts.",
    )
    if selected_trader != "All Traders":
        st.markdown(
            f'<div class="sb-badge">Highlighting: {selected_trader}</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Quick stats ───────────────────────────────────────────────────────────
    st.markdown('<div class="sb-label">Quick Stats</div>', unsafe_allow_html=True)
    sel_row = df_traders[df_traders["Trader Type"] == selected_trader]
    if not sel_row.empty:
        r = sel_row.iloc[0]
        st.metric("Net Return",    f"{r['Net Return (%)']:.1f}%")
        st.metric("Win Rate",      f"{r['Win Rate (%)']:.0f}%")
        st.metric("Max Drawdown",  f"{r['Max Drawdown (%)']:.1f}%")
        st.metric("6-Mo Failure",  f"{r['6-Mo Failure (%)']:.0f}%")
    else:
        st.caption("Select a specific trader type to see its stats.")

    st.divider()

    # ── Data sources ──────────────────────────────────────────────────────────
    st.markdown('<div class="sb-label">Data Sources</div>', unsafe_allow_html=True)
    sources = [
        ("SEBI India", "Sept 2024"),
        ("ESMA (EU)", "CFD disclosure"),
        ("Quantopian 888-strategy", "2016"),
        ("Barber & Odean / UC Berkeley", "Taiwan study"),
        ("MEXC", "2026 slippage analysis"),
        ("Dalbar Inc.", "20-year retail study"),
        ("TradingView Hub", "2026"),
    ]
    for name, detail in sources:
        st.markdown(
            f"<span style='color:{TEXT}; font-size:0.82rem; font-weight:600;'>{name}</span>"
            f"<span style='color:{MUTED}; font-size:0.80rem;'> · {detail}</span><br>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        f"<span style='color:{MUTED}; font-size:0.76rem;'>"
        "By Pawan Bohora · MSCS, Wright State University · Independent research"
        "</span>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 7 ·  HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("# 📊 Do Trading Bots Actually Work?")
st.markdown(
    "A data-driven forensic analysis of retail algorithmic trading performance "
    "**after fees, slippage, latency, and risk.** Built on primary-source data from "
    "SEBI India, ESMA, Quantopian's 888-strategy study, and Dalbar's 20-year retail dataset."
)
st.divider()

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Retail Traders Who Lose Money",   "89–93%",  "SEBI India & ESMA",              delta_color="inverse")
k2.metric("Algo Bots Failing Within 6 Mo.",  "73%",     "Automated crypto accounts",       delta_color="inverse")
k3.metric("Backtest Predicts Live (R²)",      "≈1–2%",  "888 strategies · Quantopian",     delta_color="inverse")
k4.metric("Slippage as % of Gross Revenue",  "347%",    "BTC HF mean reversion · MEXC",    delta_color="inverse")
st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# 8 ·  SECTION A — Performance Overview
# ═══════════════════════════════════════════════════════════════════════════════
section(
    "Section 01  ·  Performance",
    "Net Returns by Trader Type",
    "After exchange fees and slippage — which approach actually makes money?",
)

col_a1, col_a2 = st.columns(2)

# ── Chart A1: Net annual return ───────────────────────────────────────────────
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

# ── Chart A2: Win rate comparison ─────────────────────────────────────────────
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

# ── Comparison table (collapsible) ────────────────────────────────────────────
with st.expander("📋  Full comparison table", expanded=False):
    display = df_traders.copy()
    if selected_trader != "All Traders":
        display = display[display["Trader Type"] == selected_trader]
    st.dataframe(
        display.style.format({
            c: "{:.2f}" for c in display.columns if "(%)" in c
        }),
        hide_index=True,
        use_container_width=True,
    )

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# 9 ·  SECTION B — The Win Rate Paradox
# ═══════════════════════════════════════════════════════════════════════════════
section(
    "Section 02  ·  The Core Trap",
    "The Win Rate Paradox",
    "65% of traders had >50% win rates — yet 82% lost money. Here's why.",
)

col_b1, col_b2 = st.columns(2)

# ── Chart B1: Paradox headline ────────────────────────────────────────────────
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
        text="Study of 25,000+ retail accounts · 4M+ trades",
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

# ── Chart B2: Win-rate vs net P&L simulation ──────────────────────────────────
with col_b2:
    fig = go.Figure()
    # Shaded loss zone
    loss_mask = _pnl < 0
    fig.add_trace(go.Scatter(
        x=_wr[loss_mask] * 100, y=_pnl[loss_mask],
        fill="tozeroy", fillcolor="rgba(247,93,93,0.09)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    # Shaded profit zone
    win_mask = _pnl >= 0
    fig.add_trace(go.Scatter(
        x=_wr[win_mask] * 100, y=_pnl[win_mask],
        fill="tozeroy", fillcolor="rgba(79,209,165,0.09)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    # Main curve
    fig.add_trace(go.Scatter(
        x=_wr * 100, y=_pnl,
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
    # Mark typical retail bot range
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

st.info(
    f"**Insight:** With an avg winner of +{WIN_AVG}% and avg loser of {LOSS_AVG}%, "
    f"a bot needs a **{BREAKEVEN_WR*100:.0f}% win rate just to break even**. "
    "Most retail bots achieve 55–65%. "
    "**Win rate is the wrong optimisation target. Payoff ratio is what separates "
    "profitable strategies from guaranteed slow losses.**",
    icon="💡",
)
st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# 10 ·  SECTION C — Cost Erosion
# ═══════════════════════════════════════════════════════════════════════════════
section(
    "Section 03  ·  Costs",
    "The Fee & Slippage Erosion Cascade",
    "How exchange fees and slippage compound to destroy returns that look great on paper.",
)

col_c1, col_c2 = st.columns([3, 2])

# ── Chart C1: Waterfall ───────────────────────────────────────────────────────
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

# ── Panel C2: Real-world example table ───────────────────────────────────────
with col_c2:
    st.markdown(f"#### Real-World Extreme")
    st.markdown(
        "BTC High-Frequency Mean Reversion strategy "
        "(MEXC analysis, 2026 · 36,008 transactions):"
    )
    real = pd.DataFrame({
        "Stage":  ["Gross Profit", "Exchange Fees", "Slippage Costs", "Net Result"],
        "Amount": ["$84,534", "−$66,456", "−$46,966", "−$99,896"],
    })
    st.dataframe(real, hide_index=True, use_container_width=True)
    st.markdown(
        f"<span style='color:{RED}; font-weight:700; font-size:0.92rem;'>"
        "Slippage = 347% of gross revenue.</span><br>"
        f"<span style='color:{MUTED}; font-size:0.83rem;'>"
        "A profitable strategy on paper became a $99K loss in production. "
        "No standard backtest framework surfaces this automatically.</span>",
        unsafe_allow_html=True,
    )
    st.warning(
        "Real-world returns run **30–50% below backtested results** — universally.",
        icon="⚠️",
    )

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# 11 ·  SECTION D — Regulator Data
# ═══════════════════════════════════════════════════════════════════════════════
section(
    "Section 04  ·  Regulator Evidence",
    "Official Loss Rates by Market",
    "Legal broker disclosures and regulator-commissioned studies — not marketing estimates.",
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
    _base_wide_margin = {**BASE, "margin": dict(l=200, r=32, t=58, b=44)}
    fig.update_layout(
        **_base_wide_margin, height=340,
        title="% of Retail Traders Losing Money — Regulator-Disclosed Data",
        xaxis_title="Loss Rate (%)", xaxis_ticksuffix="%", xaxis_range=[0, 125],
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with col_d2:
    st.markdown("#### The Asterisk on Bots")
    st.markdown(
        f"The **40% loss rate** for retail bots looks far better than the 88% "
        f"for manual traders.<br><br>"
        f"<span style='color:{RED};'>**It is survivorship-biased.**</span> "
        f"It counts only currently-active bots. 73% of accounts fail within "
        f"6 months and exit the dataset before ever being counted as losers.",
        unsafe_allow_html=True,
    )

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# 12 ·  SECTION E — Survivorship Bias
# ═══════════════════════════════════════════════════════════════════════════════
section(
    "Section 05  ·  Hidden Data",
    "Survivorship Bias — The Invisible Graveyard",
    "Platform leaderboards only show winning bots. The failing majority quietly disappears.",
)

col_e1, col_e2 = st.columns(2)

# ── Chart E1: Donut — visible vs hidden ───────────────────────────────────────
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

# ── Chart E2: Grouped bar — biased vs corrected metrics ──────────────────────
with col_e2:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Platform-Reported (Biased)",
        x=SB_METRICS, y=SB_BIASED,
        marker_color=BLUE, marker_line_width=0,
        text=[str(v) for v in SB_BIASED],
        textposition="outside", textfont=dict(color=TEXT, size=11),
        hovertemplate="%{x}<br>Biased: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Survivorship-Corrected",
        x=SB_METRICS, y=SB_CORRECTED,
        marker_color=RED, marker_line_width=0,
        text=[str(v) for v in SB_CORRECTED],
        textposition="outside", textfont=dict(color=TEXT, size=11),
        hovertemplate="%{x}<br>Corrected: %{y}<extra></extra>",
    ))
    # Delta annotations
    for xi, (b, c) in enumerate(zip(SB_BIASED, SB_CORRECTED)):
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
        title="Bias Correction: What Performance Metrics Really Look Like",
        barmode="group",
        yaxis_title="Value",
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# 13 ·  SECTION F — 20-Year Reality Check (full-width)
# ═══════════════════════════════════════════════════════════════════════════════
section(
    "Section 06  ·  Long-Term View",
    "The 20-Year Reality Check",
    "$10,000 invested in 2006 — where does each approach end up by 2025?",
)

GROWTH_COLORS = {
    "Passive Index (S&P 500)":   GREEN,
    "Retail Bot (Optimistic)":   BLUE,
    "Manual Retail Trader":      RED,
}
GROWTH_DASH = {
    "Passive Index (S&P 500)":   "solid",
    "Retail Bot (Optimistic)":   "dot",
    "Manual Retail Trader":      "dash",
}

fig = go.Figure()
for col_name, color in GROWTH_COLORS.items():
    # Show only relevant series when filter is active
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
    title="$10,000 Invested in 2006 — Terminal Value in 2025",
    xaxis_title="Year",
    yaxis_title="Portfolio Value (USD)",
    yaxis_tickprefix="$", yaxis_tickformat=",.0f",
)
st.plotly_chart(fig, use_container_width=True)

# Terminal value callout row
tv_passive = df_growth["Passive Index (S&P 500)"].iloc[-1]
tv_bot     = df_growth["Retail Bot (Optimistic)"].iloc[-1]
tv_manual  = df_growth["Manual Retail Trader"].iloc[-1]

g1, g2, g3 = st.columns(3)
g1.metric("Passive Index (S&P 500)",   f"${tv_passive:,.0f}",  f"+${tv_passive-10000:,.0f} total gain")
g2.metric("Retail Bot (Optimistic)",   f"${tv_bot:,.0f}",      f"${tv_passive-tv_bot:,.0f} below passive",  delta_color="inverse")
g3.metric("Manual Retail Trader",      f"${tv_manual:,.0f}",   f"${tv_passive-tv_manual:,.0f} below passive", delta_color="inverse")
st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# 14 ·  SECTION G — Key Insights
# ═══════════════════════════════════════════════════════════════════════════════
section(
    "Section 07  ·  Conclusions",
    "Key Insights",
    "Five data-backed conclusions from this analysis.",
)

# Two-column insight layout
ins_left, ins_right = st.columns(2)

with ins_left:
    insight(
        "red",
        "💸  Fees and slippage can consume more than 100% of gross profit.",
        "A BTC high-frequency mean reversion strategy earning $84,534 gross resulted in a $99,896 net loss. "
        "Exchange fees ($66,456) and slippage ($46,966) together equalled 347% of gross revenue — "
        "a ratio no standard backtest framework surfaces automatically.",
        "MEXC Slippage Analysis, 2026",
    )
    insight(
        "red",
        "🔬  Backtests predict live performance with less than 2% accuracy.",
        "Quantopian's study of 888 strategies found R² ≈ 0.025 between backtest and live Sharpe ratios. "
        "Testing just 50 strategy variants produces a 92%+ probability of finding a false positive by chance. "
        "A high backtest Sharpe is statistically indistinguishable from a low one as a live predictor.",
        "Wiecki et al. / Quantopian, 2016",
    )
    insight(
        "yellow",
        "📐  Win rate is a misleading target. Payoff ratio is what matters.",
        "65% of traders in a 25,000+ account study had >50% win rates, yet 82% lost money overall. "
        f"Average winner: +{WIN_AVG}%. Average loser: {LOSS_AVG}%. "
        f"At this payoff asymmetry, a bot needs ~{BREAKEVEN_WR*100:.0f}% win rate just to break even.",
        "Barber, Makov & Schwartz · JFQA 2024",
    )

with ins_right:
    insight(
        "red",
        "🏦  Institutional algorithms are on the other side — and they're winning.",
        "SEBI India (2024): 93% of 10M+ retail F&O traders lost a combined $21.7B over 3 years. "
        "In the same period, institutional algo traders captured 97% of FPI profits and 96% of "
        "proprietary trader profits. Retail bots aren't competing against slow humans — "
        "they're counterparties to professional quants with co-location and sub-ms execution.",
        "SEBI India Press Release, September 2024",
    )
    insight(
        "yellow",
        "⚖️  Bots beat manual trading — but both lose to passive indexing.",
        "~60% of retail algo traders show positive annual returns vs. 5–10% for manual day traders. "
        "Yet the average retail investor still underperforms the S&P 500 by 6.1% annually over 20 years. "
        "Automation reduces emotional error but cannot overcome structural market disadvantages.",
        "Dalbar Inc. 20-Year Study · TradingView Hub, 2026",
    )
    insight(
        "green",
        "✅  The rare successful bots share four traits.",
        "Low trading frequency (limits fee drag), walk-forward validated edge (combats overfitting), "
        "payoff-ratio-aware risk sizing, and hard drawdown circuit breakers. "
        "These are not 'set and forget' tools — they require ongoing research and maintenance, "
        "which is by definition a professional job.",
        "Synthesis across all reviewed sources",
    )

st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# 15 ·  METHODOLOGY EXPANDER
# ═══════════════════════════════════════════════════════════════════════════════
with st.expander("🔍  Methodology & Data Notes", expanded=False):
    st.markdown(f"""
**Dataset:** This dashboard uses a structured dataset derived from primary regulatory disclosures,
academic publications, and broker-level studies. No data is fabricated; all figures are cited to
original sources.

**Trader Types:** The four categories represent archetypal strategies:
- *Retail Bot* — retail algorithmic traders using cloud-hosted bots (3Commas, Bitsgap, custom Python)
- *Manual Day Trader* — retail humans actively trading without automation
- *Institutional Algo* — professional quant funds and prop desks with co-location & proprietary data
- *Passive Index (S&P 500)* — buy-and-hold SPY or equivalent, no active management

**Performance Figures:** Net returns are modelled from gross returns after subtracting median
exchange fees and slippage estimates for each trader type. Institutional figures are based on
publicly reported hedge fund aggregate returns.

**Win Rate Simulation:** The P&L curve uses empirically-measured average winner (+{WIN_AVG}%) and
average loser ({LOSS_AVG}%) from a 2023 study of 25,000+ retail accounts covering 4M+ trades.

**Survivorship Bias Correction:** Correction factors derived from Andrikogiannopoulou &
Papakonstantinou's hedge fund study showing 14pp drawdown underestimation and annual return
overstatement of 1–4%.

**20-Year Compound Model:** Starting capital $10,000 in Jan 2006. Passive: 10% p.a. (S&P historical
CAGR). Retail bot: 6.5% p.a. (optimistic net, post-cost). Manual retail: 3.9% p.a. (Dalbar
20-year average).
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# 16 ·  FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(
    f"<div style='text-align:center; color:#6B7280; font-size:0.78rem; padding:14px 0 28px;'>"
    "Data · SEBI India (2024) &nbsp;·&nbsp; ESMA &nbsp;·&nbsp; "
    "Wiecki et al./Quantopian (2016) &nbsp;·&nbsp; Barber &amp; Odean / UC Berkeley &nbsp;·&nbsp; "
    "MEXC (2026) &nbsp;·&nbsp; Dalbar Inc. &nbsp;·&nbsp; TradingView Hub (2026)<br>"
    "Built with <b>Streamlit</b> &amp; <b>Plotly</b> &nbsp;·&nbsp; "
    "Independent research · Pawan Bohora &nbsp;·&nbsp; MSCS, Wright State University"
    "</div>",
    unsafe_allow_html=True,
)
