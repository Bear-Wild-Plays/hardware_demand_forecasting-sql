import os
import sqlite3
import numpy as np
import pandas as pd

os.makedirs("data", exist_ok=True)
np.random.seed(42)

# 156 weeks (3 years of weekly POS, shipments, inventory, and baseline forecasts)
weeks = pd.date_range(start="2024-01-01", periods=156, freq="W-MON")

skus = [
    {
        "sku_id": "HW-VR-PRO-256",
        "product_name": "Horizon VR Pro Headset (256GB)",
        "category": "VR Hardware",
        "unit_cost": 320.00,
        "retail_price": 499.99,
        "base_weekly_demand": 4200,
        "launch_week_idx": 0,
    },
    {
        "sku_id": "HW-SG-RAY-01",
        "product_name": "Aura Smart Glasses Gen 2",
        "category": "Wearables",
        "unit_cost": 185.00,
        "retail_price": 299.99,
        "base_weekly_demand": 3100,
        "launch_week_idx": 0,
    },
    {
        "sku_id": "HW-VR-LITE-128",
        "product_name": "Horizon VR Lite (128GB) - NPI",
        "category": "VR Hardware",
        "unit_cost": 195.00,
        "retail_price": 299.99,
        "base_weekly_demand": 5800,
        "launch_week_idx": 104,  # Launched Year 3 (New Product Introduction)
    },
    {
        "sku_id": "HW-ACC-DOCK-02",
        "product_name": "Magnetic Charging Dock",
        "category": "Accessories",
        "unit_cost": 28.00,
        "retail_price": 69.99,
        "base_weekly_demand": 2600,
        "launch_week_idx": 0,
    },
]

records = []

for sku in skus:
    on_hand = sku["base_weekly_demand"] * 6  # Start with 6 weeks of supply
    for idx, week_date in enumerate(weeks):
        if idx < sku["launch_week_idx"]:
            continue

        week_of_year = week_date.isocalendar().week
        tenure_weeks = idx - sku["launch_week_idx"]

        # NPI ramp curve for newly launched hardware
        npi_multiplier = min(1.0, 0.45 + (tenure_weeks * 0.06)) if sku["launch_week_idx"] > 0 else 1.0

        # Q4 Holiday Seasonality (Weeks 45-52) & Back-to-School bump (Weeks 32-35)
        seasonality = 1.0
        if 45 <= week_of_year <= 52:
            seasonality = 1.65 + (0.15 if week_of_year in [47, 48] else 0.0)
        elif 32 <= week_of_year <= 35:
            seasonality = 1.18
        elif 5 <= week_of_year <= 10:
            seasonality = 0.85

        # Promotional calendar events (Prime/Summer Promo wk 28, Black Friday wk 47-48)
        is_promo = 1 if week_of_year in [28, 47, 48] else 0
        promo_lift = 1.35 if is_promo else 1.0

        # True underlying demand + realistic market noise
        expected_demand = sku["base_weekly_demand"] * npi_multiplier * seasonality * promo_lift
        actual_pos_units = int(max(0, np.random.normal(expected_demand, expected_demand * 0.08)))

        # Prior consensus forecast (intentionally slightly biased during promos/NPI for variance analysis)
        forecast_noise = np.random.normal(0.94 if is_promo else 1.02, 0.06)
        consensus_forecast_units = int(max(0, expected_demand * forecast_noise))

        # Replenishment shipments & ending channel inventory
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
df.to_csv("data/hardware_demand_history.csv", index=False)

conn = sqlite3.connect("data/hardware_supply_chain.db")
df.to_sql("weekly_demand_fact", conn, if_exists="replace", index=False)
conn.close()

print(f"Generated {len(df):,} weekly SKU records into data/hardware_supply_chain.db")