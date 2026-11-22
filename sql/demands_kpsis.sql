-- ============================================================================
-- Enterprise Hardware Demand Planning & Inventory Health Queries
-- Dialect: SQLite / Standard ANSI SQL
-- ============================================================================

-- 1. SKU-Level Forecast Accuracy (MAPE, WMAPE & Bias) for Most Recent Quarter
WITH recent_quarter AS (
    SELECT
        sku_id,
        product_name,
        category,
        week_start_date,
        is_promo,
        actual_pos_units,
        consensus_forecast_units,
        (consensus_forecast_units - actual_pos_units) AS forecast_error_units,
        ABS(consensus_forecast_units - actual_pos_units) AS abs_error_units
    FROM weekly_demand_fact
    WHERE week_start_date >= date((SELECT MAX(week_start_date) FROM weekly_demand_fact), '-91 days')
)
SELECT
    sku_id,
    product_name,
    category,
    COUNT(*) AS weeks_measured,
    SUM(actual_pos_units) AS total_actual_pos,
    SUM(consensus_forecast_units) AS total_forecast,
    ROUND(AVG(CAST(abs_error_units AS FLOAT) / NULLIF(actual_pos_units, 0)) * 100, 2) AS mape_pct,
    ROUND((CAST(SUM(abs_error_units) AS FLOAT) / NULLIF(SUM(actual_pos_units), 0)) * 100, 2) AS wmape_pct,
    ROUND((CAST(SUM(forecast_error_units) AS FLOAT) / NULLIF(SUM(actual_pos_units), 0)) * 100, 2) AS forecast_bias_pct
FROM recent_quarter
GROUP BY sku_id, product_name, category
ORDER BY wmape_pct DESC;


-- 2. Rolling 4-Week Sell-Through & Channel Weeks-of-Supply (WOS) Exception Report
WITH rolling_metrics AS (
    SELECT
        week_start_date,
        sku_id,
        product_name,
        category,
        actual_pos_units,
        ending_channel_inventory,
        ROUND(AVG(actual_pos_units) OVER (
            PARTITION BY sku_id
            ORDER BY week_start_date
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ), 1) AS rolling_4wk_avg_pos,
        LAG(actual_pos_units, 1) OVER (
            PARTITION BY sku_id
            ORDER BY week_start_date
        ) AS prior_week_pos
    FROM weekly_demand_fact
),
latest_snapshot AS (
    SELECT
        *,
        ROUND(CAST(ending_channel_inventory AS FLOAT) / NULLIF(rolling_4wk_avg_pos, 0), 2) AS weeks_of_supply,
        ROUND(((CAST(actual_pos_units - prior_week_pos AS FLOAT)) / NULLIF(prior_week_pos, 0)) * 100, 1) AS wow_pos_growth_pct
    FROM rolling_metrics
    WHERE week_start_date = (SELECT MAX(week_start_date) FROM weekly_demand_fact)
)
SELECT
    sku_id,
    product_name,
    actual_pos_units AS latest_wk_pos,
    rolling_4wk_avg_pos,
    wow_pos_growth_pct,
    ending_channel_inventory,
    weeks_of_supply,
    CASE
        WHEN weeks_of_supply < 3.0 THEN 'STOCKOUT_RISK (< 3 WOS)'
        WHEN weeks_of_supply > 8.0 THEN 'EXCESS_INVENTORY (> 8 WOS)'
        ELSE 'HEALTHY (3-8 WOS)'
    END AS inventory_health_flag
FROM latest_snapshot
ORDER BY weeks_of_supply ASC;