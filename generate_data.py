import os
import sqlite3
import numpy as np
import pandas as pd

os.makedirs("data", exist_ok=True)
np.random.seed(42)

# 156 weeks (3 years of weekly village consumption, harvests, inventory, and baseline forecasts)
weeks = pd.date_range(start="2024-01-01", periods=156, freq="W-MON")

skus = [
    {
        "sku_id": "SMF-BRY-PRO-256",
        "product_name": "Reserve Smurfberry Harvest Crate (256-Count)",
        "category": "Core Staples",
        "unit_cost": 12.50,
        "retail_price": 24.99,
        "base_weekly_demand": 4200,
        "launch_week_idx": 0,
    },
    {
        "sku_id": "SMF-CAP-WHT-01",
        "product_name": "Standard Issue White Phrygian Cap",
        "category": "Apparel & Gear",
        "unit_cost": 8.00,
        "retail_price": 19.99,
        "base_weekly_demand": 3100,
        "launch_week_idx": 0,
    },
    {
        "sku_id": "SMF-HND-CLK-128",
        "product_name": "Handy Smurf Automated Acorn Harvester (NPI)",
        "category": "Village Hardware",
        "unit_cost": 45.00,
        "retail_price": 89.99,
        "base_weekly_demand": 5800,
        "launch_week_idx": 104,  # Year 3 New Product Introduction
    },
    {
        "sku_id": "SMF-FRS-SUP-02",
        "product_name": "Sarsaparilla Leaf Elixir Pack",
        "category": "Provisions",
        "unit_cost": 5.50,
        "retail_price": 14.99,
        "base_weekly_demand": 2600,
        "launch_week_idx": 0,
    },
]

records = []

for sku in skus:
    on_hand = sku["base_weekly_demand"] * 6  # Start with 6 weeks of cellar supply
    for idx, week_date in enumerate(weeks):
        if idx < sku["launch_week_idx"]:
            continue

        week_of_year = week_date.isocalendar().week
        tenure_weeks = idx - sku["launch_week_idx"]

        # NPI ramp curve for Handy Smurf's new inventions
        npi_multiplier = min(1.0, 0.45 + (tenure_weeks * 0.06)) if sku["launch_week_idx"] > 0 else 1.0

        # Q4 Winter Solstice Seasonality (Weeks 45-52) & Summer Harvest bump (Weeks 32-35)
        seasonality = 1.0
        if 45 <= week_of_year <= 52:
            seasonality = 1.65 + (0.15 if week_of_year in [47, 48] else 0.0)
        elif 32 <= week_of_year <= 35:
            seasonality = 1.18
        elif 5 <= week_of_year <= 10:
            seasonality = 0.85

        # Smurfberry Festival promotional weeks (Summer Festival wk 28, Solstice Feast wk 47-48)
        is_promo = 1 if week_of_year in [28, 47, 48] else 0
        promo_lift = 1.35 if is_promo else 1.0

        # True underlying village demand + realistic forest noise
        expected_demand = sku["base_weekly_demand"] * npi_multiplier * seasonality * promo_lift
        actual_pos_units = int(max(0, np.random.normal(expected_demand, expected_demand * 0.08)))

        # Prior consensus forecast (intentionally slightly biased during festivals/NPI for variance audit)
        forecast_noise = np.random.normal(0.94 if is_promo else 1.02, 0.06)
        consensus_forecast_units = int(max(0, expected_demand * forecast_noise))

        # Replenishment harvests & ending mushroom-cellar inventory
        replenishment_units = int(consensus_forecast_units * np.random.uniform(0.95, 1.08))
        on_hand = max(0, on_hand + replenishment_units - actual_pos_units)

        records.append({
            "week_start_date": week_date.strftime("%Y-%m-%d"),
            "fiscal_year": week_date.year,
            "week_of_year": int(week_of_year),
            "sku_id": sku["sku_id"],
            "product_name": sku["product_name"],
            "category": sku["category"],
            "is_promo": is_promo,
            "actual_pos_units": actual_pos_units,
            "consensus_forecast_units": consensus_forecast_units,
            "replenishment_shipments": replenishment_units,
            "ending_channel_inventory": on_hand,
            "unit_cost": sku["unit_cost"],
            "retail_price": sku["retail_price"],
        })

df = pd.DataFrame(records)
df.to_csv("data/smurf_village_demand_history.csv", index=False)

conn = sqlite3.connect("data/smurf_village_supply_chain.db")
df.to_sql("weekly_demand_fact", conn, if_exists="replace", index=False)
conn.close()
print(f"Generated {len(df):,} weekly Smurf Village SKU records into data/smurf_village_supply_chain.db")
