#### 🍄 Smurf Village Demand Forecasting & SQL Pipeline

**An end-to-end forest supply chain demand planning pipeline combining SQL KPI & variance analytics (MAPE, WMAPE, Forecast Bias, Weeks-of-Supply), Python time-series forecasting with scenario sensitivity modeling, and grounded LLM S&OP executive reporting for Papa Smurf's village council.** 

 

#### 🎯 Project Overview

Effective Smurf Village demand planning requires translating noisy forest consumption signals, **Smurfberry Festival** promotional calendars, and **New Product Introduction (NPI)** curves (such as Handy Smurf’s latest clockwork contraptions) into reliable mushroom-warehouse positioning and capacity commitments—without letting Greedy Smurf cause a village-wide stockout or Gargamel disrupt inbound logistics. 

This repository demonstrates a production-style **Strategic Analytics & Demand Planning workflow** built for high-stakes forest operations: 

1. **Synthetic Village Consumption & NPI Data Engine (generate_data.py):** Simulates 3 years (156 weeks) of weekly village consumption, consensus forecasts, replenishment harvests, and mushroom-cellar inventory across flagship village SKUs—modeling Q4 Winter Solstice seasonality, Smurfberry Festival lift events, and NPI adoption ramps.
2. **SQL KPI & Exception Layer (sql/demand_kpis.sql):** Uses Common Table Expressions (CTEs) and SQL Window Functions (AVG OVER, LAG) to compute: 

  * **MAPE** (Mean Absolute Percentage Error) & **WMAPE** (Weighted MAPE)
  * **Forecast Bias %** (detecting systematic over-forecasting by Brainy Smurf vs. under-forecasting during Hefty Smurf’s training seasons)
  * **Rolling 4-Week Consumption & Cellar Weeks-of-Supply (WOS)** with automated STOCKOUT_RISK (< 3 WOS) and EXCESS_INVENTORY (> 8 WOS) exception flags.
3. **Statistical Forecasting & Scenario Modeling (forecast_model.py):** Fits a seasonal **Holt-Winters Exponential Smoothing** model with out-of-sample backtesting and generates a 12-week forward forecast across three S&OP planning scenarios: 

  * *Baseline Statistical Forecast*
  * *Upside Smurfberry Festival Lift (+25%)*
  * *Gargamel & Azrael Supply Route Disruption (-15%)*
4. **Grounded AI S&OP Commentary (prompts/sop_analyst_prompt.py):** Decoupled prompt engineering module with strict JSON schema enforcement and anti-hallucination guardrails that converts SQL variance tables into executive-ready S&OP briefings for Papa Smurf.

#### 🏗 Pipeline Architecture

Show Code

Hide Code

Download diagram SVG

ASCII

Weekly Village Consumption, Harvests & Inventory Data (SQLite / CSV)
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 1: SQL Extraction & KPI Layer (sql/demand_kpis.sql)        │
│  • CTEs & Window Functions (Rolling 4-Wk Consumption, WoW %)     │
│  • Forecast Accuracy Audit: MAPE, WMAPE & Bias %                 │
│  • Cellar Inventory Exception Flags (< 3 WOS / > 8 WOS)          │
└──────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
┌───────────────────────────────┐ ┌────────────────────────────────┐
│ Stage 2: Statistical Forecast │ │ Stage 3: AI S&OP Briefing      │
│ (forecast_model.py)           │ │ (prompts/sop_analyst_prompt.py)│
│  • Holt-Winters Seasonal Fit  │ │  • Grounded JSON Payload       │
│  • 12-Wk Out-of-Sample MAPE   │ │  • Strict Schema Guardrails    │
│  • Festival & Gargamel Runs   │ │  • Papa Smurf Root-Cause Notes │
└───────────────────────────────┘ └────────────────────────────────┘

Use code with caution.

Copy code text to clipboard.

#### 📦 Sample Village SKU Catalog

SKU IDVillage ItemCategoryPlanning Complexity
**SMF-BRY-PRO-256**
Reserve Smurfberry Harvest Crate (256-Count)Core StaplesHigh Q4 Solstice & Festival seasonality
**SMF-CAP-WHT-01**
Standard Issue White Phrygian CapApparel & GearSteady baseline + Hefty Smurf wear-and-tear
**SMF-HND-CLK-128**
Handy Smurf’s Automated Acorn Harvester (NPI)Village HardwareYear 3 New Product Introduction ramp curve
**SMF-FRS-SUP-02**
Sarsaparilla Leaf Elixir PackProvisionsHigh promo sensitivity during village dances

#### 🚀 Quickstart

bash

# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate the 3-year Smurf Village supply chain SQLite database & CSVs
python generate_data.py

# 3. Run the SQL KPI audit & 12-week statistical forecast scenarios
python forecast_model.py

Use code with caution.

Copy code text to clipboard.

#### 👤 Author

**Sean David Wilda** — Supply Chain & Strategic Planning Specialist | AI Product Quality & Analytics
[LinkedIn](https://www.linkedin.com/in/sean-wilda-196a2713/) · [GitHub](https://github.com/Bear-Wild-Plays) · [Portfolio](https://www.bearwildplays.com)
