# 📊 Hardware Demand Forecasting & SQL Pipeline

**An end-to-end consumer hardware demand planning pipeline combining SQL KPI & variance analytics (MAPE, WMAPE, Forecast Bias, Weeks-of-Supply), Python time-series forecasting with scenario sensitivity modeling, and grounded LLM S&OP executive reporting.**

![Python](https://shields.io)
![SQL](https://shields.io)
![Statsmodels](https://shields.io)

---

## 🎯 Project Overview

Effective hardware demand planning requires translating noisy point-of-sale (POS) signals, promotional calendars, and New Product Introduction (NPI) curves into reliable inventory positioning and capacity commitments.

This repository demonstrates a production-style **Strategic Analytics & Demand Planning workflow**:

1. **Synthetic Hardware POS & NPI Data Engine (`generate_data.py`):** Simulates 3 years (156 weeks) of weekly sell-through, consensus forecasts, replenishment shipments, and channel inventory across flagship hardware SKUs—modeling Q4 holiday seasonality, promotional lift events, and NPI adoption ramps.
2. **SQL KPI & Exception Layer (`sql/demand_kpis.sql`):** Uses Common Table Expressions (CTEs) and SQL Window Functions (`AVG OVER`, `LAG`) to compute:
   - **MAPE** (Mean Absolute Percentage Error) & **WMAPE** (Weighted MAPE)
   - **Forecast Bias %** (detecting systematic over- vs. under-forecasting)
   - **Rolling 4-Week Sell-Through & Channel Weeks-of-Supply (WOS)** with automated `STOCKOUT_RISK` (< 3 WOS) and `EXCESS_INVENTORY` (> 8 WOS) exception flags.
3. **Statistical Forecasting & Scenario Modeling (`forecast_model.py`):** Fits a seasonal **Holt-Winters Exponential Smoothing** model with out-of-sample backtesting and generates a 12-week forward forecast across three S&OP planning scenarios:
   - *Baseline Statistical Forecast*
   - *Upside Promotional Lift (+25%)*
   - *Component Supply Constraint (-15%)*
4. **Grounded AI S&OP Commentary (`prompts/sop_analyst_prompt.py`):** Decoupled prompt engineering module with strict JSON schema enforcement and anti-hallucination guardrails that converts SQL variance tables into executive-ready S&OP action items.

---

## 🏗 Pipeline Architecture

```text
Weekly POS, Shipments & Inventory Data (SQLite / CSV)
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│ Stage 1: SQL Extraction & KPI Layer (sql/demand_kpis.sql)│
│  • CTEs & Window Functions (Rolling 4-Wk POS, WoW %)     │
│  • Forecast Accuracy Audit: MAPE, WMAPE & Bias %         │
│  • Channel Inventory Exception Flags (<3 WOS / >8 WOS)   │
└──────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
┌───────────────────────────────┐ ┌────────────────────────────────┐
│ Stage 2: Statistical Forecast │ │ Stage 3: AI S&OP Briefing      │
│ (forecast_model.py)           │ │ (prompts/sop_analyst_prompt.py)│
│  • Holt-Winters Seasonal Fit  │ │  • Grounded JSON Payload       │
│  • 12-Wk Out-of-Sample MAPE   │ │  • Strict Schema Guardrails    │
│  • Promo & Supply Scenarios   │ │  • Executive Root-Cause Notes  │
└───────────────────────────────┘ └────────────────────────────────┘
```

---

## 🚀 Quickstart

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate the 3-year hardware supply chain SQLite database & CSVs
python generate_data.py

# 3. Run the SQL KPI audit & 12-week statistical forecast scenarios
python forecast_model.py
```

---

## 👤 Author
**Sean David Wilda** — Supply Chain & Strategic Planning Specialist | AI Product Quality & Analytics  
[LinkedIn](https://linkedin.com) · [GitHub](https://github.com) · [Portfolio](https://bearwildplays.com)