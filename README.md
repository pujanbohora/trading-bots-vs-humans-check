# Trading Bots: Reality Check 

> A data-driven forensic analysis of whether retail algorithmic trading bots outperform human traders — after accounting for fees, slippage, latency, and risk.

**Stack:** Python · Streamlit · Plotly · Pandas · NumPy

---

## Overview

Most retail trading bot documentation focuses on backtested returns and strategy logic. This project asks a harder question: **do these bots actually work in production?**

I analyzed data from regulators (SEBI India, ESMA), academic research (Quantopian 888-strategy study, Barber & Odean), and broker-level cost studies (MEXC 2026) to build a structured picture of retail algo trading economics. The findings are visualized in an interactive Streamlit dashboard with a sidebar trader-type filter, section-level provenance tags, and a full methodology disclosure.

**This is a portfolio project** — it demonstrates data analysis, visualization design, and quantitative reasoning. It is not a trading recommendation or a production system.

---

## Key Findings

| Finding | Value | Source |
|---------|-------|--------|
| Retail traders who lose money | 89–93% | SEBI India 2024; ESMA |
| Algo bots failing within 6 months | 73% | ForTraders 2026 |
| Backtest → live Sharpe R² | ≈ 0.025 | Wiecki et al. / Quantopian, 888 strategies |
| Strategy earning $84K gross netted −$99K after fees | 347% slippage | MEXC slippage analysis, 2026 |
| Traders with >50% win rate who still lost money | 82% | Barber, Makov & Schwartz · JFQA 2024 |
| Retail investor underperforms S&P 500 annually | 6.1% over 20 years | Dalbar Inc. |
| Institutional algo share of FPI profits (India) | 97% | SEBI India, Sept 2024 |

---

## Dashboard Preview

![Dashboard preview](assets/dashboard-preview.png)

*Dark-themed Streamlit dashboard with sidebar trader-type filter, KPI hero row, 8 chart sections, and a full methodology disclosure.*

---

## Methodology / Data Notes

This dashboard uses a **deliberate mix of source-cited data and modelled scenarios**, tagged throughout the UI:

| Tag | Meaning |
|-----|---------|
| **SOURCE** | Directly cited from regulatory disclosures or peer-reviewed studies |
| **MODELED** | Derived or calculated from source figures (e.g., net return = gross − fees − slippage) |
| **ILLUSTRATIVE** | Scenario model built to explain a concept; all assumptions stated explicitly |

All major conclusions are anchored to cited primary sources. Modelled values exist only to make the mechanics visually interpretable — not to fabricate unsupported claims.

See the in-app **Methodology & Data Notes** expander for a complete breakdown of every data point and its provenance.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Core language |
| Streamlit | Dashboard framework |
| Plotly | Interactive charts |
| Pandas | Data modelling |
| NumPy | Win-rate simulation |

---

## How to Run

```bash
git clone https://github.com/pujanbohora/trading-bots-vs-humans-check.git
cd trading-bots-reality-check
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Repo Structure

```
trading-bots-reality-check/
├── app.py                    # Dashboard: data layer + UI (clearly separated)
├── requirements.txt          # Python dependencies
├── README.md
├── .gitignore
├── assets/
│   └── dashboard-preview.png # Screenshot for README / portfolio
└── docs/
    └── extended-analysis.pdf # Full written analysis with citations
```

**`app.py` is organized into clearly separated layers:**
- **Design system** — colour tokens, chart defaults, CSS
- **Data layer** — `load_data()`, `build_win_rate_model()`, `build_growth_model()`
- **UI helpers** — `render_section_header()`, `render_insight_card()`, `source_note()`
- **Dashboard sections** — §01–§10, each self-contained

---

## Dashboard Sections

| Section | Content |
|---------|---------|
| §01 · Performance | Net returns and win rates by trader type |
| §02 · The Core Trap | Win rate paradox — 65% win rate, 82% lose money |
| §03 · Costs | Fee & slippage erosion waterfall + MEXC real-world case |
| §04 · Regulator Evidence | Official loss rates from SEBI, ESMA, CFTC, Barber & Odean |
| §05 · Hidden Data | Survivorship bias — the invisible graveyard |
| §06 · Long-Term View | 20-year $10K compound growth comparison |
| §07 · Findings | 5 insight cards with source citations |
| §08 · Conclusion | 3 key takeaways, implications, future work |
| §09 · Methodology | Full data provenance breakdown (SOURCE / MODELED / ILLUS) |

---

## Future Improvements

- Live broker API integration (Alpaca / Interactive Brokers) for real performance data
- Per-strategy backtesting module with walk-forward validation
- Slippage and execution cost modelling by asset class and trade frequency
- Monte Carlo simulation for strategy robustness and parameter sensitivity
- Comparison with professional CTA/quant fund benchmarks (Barclay CTA Index)

---

## Author

**Pawan Bohora** — MSCS, Wright State University  
Independent research portfolio project

[GitHub](https://github.com/pawanbohora) · [LinkedIn](https://linkedin.com/in/pawanbohora)
