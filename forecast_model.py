import sqlite3
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_percentage_error

DB_PATH = "data/hardware_supply_chain.db"


def run_sql_kpi_audit(conn: sqlite3.Connection) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Executes analytical SQL queries to extract MAPE/Bias and WOS exception flags."""
    with open("sql/demand_kpis.sql", "r", encoding="utf-8") as f:
        raw_sql = f.read()

    # Split statements safely
    statements = [s.strip() for s in raw_sql.split(";") if s.strip() and not s.strip().startswith("--")]
    accuracy_df = pd.read_sql_query(statements[0], conn)
    inventory_df = pd.read_sql_query(statements[1], conn)
    return accuracy_df, inventory_df


def generate_statistical_forecast(conn: sqlite3.Connection, sku_id: str, horizon_weeks: int = 12) -> pd.DataFrame:
    """Fits a Holt-Winters seasonal model and generates baseline + scenario forecasts."""
    query = """
        SELECT week_start_date, actual_pos_units, is_promo
        FROM weekly_demand_fact
        WHERE sku_id = ?
        ORDER BY week_start_date ASC
    """
    df = pd.read_sql_query(query, conn, params=(sku_id,))
    df["week_start_date"] = pd.to_datetime(df["week_start_date"])
    df = df.set_index("week_start_date").asfreq("W-MON")

    # Train/Test split (hold out last 12 weeks for out-of-sample backtesting)
    train = df["actual_pos_units"].iloc[:-horizon_weeks]
    test = df["actual_pos_units"].iloc[-horizon_weeks:]

    model = ExponentialSmoothing(
        train,
        trend="add",
        seasonal="add",
        seasonal_periods=52,
        initialization_method="estimated",
    ).fit()

    val_preds = model.forecast(horizon_weeks)
    holdout_mape = mean_absolute_percentage_error(test, val_preds) * 100

    # Refit on full history for forward 12-week S&OP forecast
    full_model = ExponentialSmoothing(
        df["actual_pos_units"],
        trend="add",
        seasonal="add",
        seasonal_periods=52,
        initialization_method="estimated",
    ).fit()

    future_baseline = full_model.forecast(horizon_weeks).round().astype(int)

    forecast_df = pd.DataFrame({
        "forecast_week": future_baseline.index.strftime("%Y-%m-%d"),
        "sku_id": sku_id,
        "baseline_stat_forecast": future_baseline.values,
        "upside_promo_scenario_plus_25pct": (future_baseline.values * 1.25).round().astype(int),
        "supply_constrained_scenario_minus_15pct": (future_baseline.values * 0.85).round().astype(int),
        "backtest_holdout_mape_pct": round(holdout_mape, 2),
    })
    return forecast_df


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    accuracy_df, inventory_df = run_sql_kpi_audit(conn)

    print("\n=== QTD FORECAST ACCURACY & BIAS (SQL OUTPUT) ===")
    print(accuracy_df.to_string(index=False))

    print("\n=== CHANNEL INVENTORY & WEEKS-OF-SUPPLY EXCEPTIONS (SQL OUTPUT) ===")
    print(inventory_df.to_string(index=False))

    print("\n=== 12-WEEK STATISTICAL FORECAST & SCENARIO SENSITIVITY (HW-VR-PRO-256) ===")
    fcst = generate_statistical_forecast(conn, "HW-VR-PRO-256", horizon_weeks=12)
    print(fcst.to_string(index=False))

    fcst.to_csv("data/vr_pro_12wk_forecast_scenarios.csv", index=False)
    conn.close()