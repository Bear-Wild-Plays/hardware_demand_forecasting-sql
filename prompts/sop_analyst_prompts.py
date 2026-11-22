import json

SOP_SYSTEM_PROMPT = """
You are a Senior Strategic Demand Planning Analyst preparing an executive briefing
for a monthly Sales & Operations Planning (S&OP) review.

STRICT GROUNDING & QUALITY RULES:
1. Rely EXCLUSIVELY on the structured SQL KPI metrics and forecast numbers provided in the user payload.
2. Never invent external market events, SKU numbers, or percentages not present in the data.
3. Explicitly distinguish between positive forecast bias (over-forecasting / excess risk)
   and negative forecast bias (under-forecasting / stockout risk).
4. Return your response strictly adhering to the required JSON schema.
"""

SOP_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "executive_headline": {"type": "string"},
        "top_forecast_error_drivers": {
            "type": "array",
            "items": {"type": "string"},
        },
        "inventory_exception_actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sku_id": {"type": "string"},
                    "status": {"type": "string"},
                    "recommended_action": {"type": "string"},
                },
                "required": ["sku_id", "status", "recommended_action"],
            },
        },
        "data_confidence_check": {"type": "string"},
    },
    "required": [
        "executive_headline",
        "top_forecast_error_drivers",
        "inventory_exception_actions",
        "data_confidence_check",
    ],
}


def build_sop_briefing_prompt(accuracy_records: list[dict], inventory_records: list[dict]) -> str:
    """Constructs a deterministic, grounded prompt payload from SQL query results."""
    payload = {
        "qtd_forecast_accuracy": accuracy_records,
        "latest_inventory_health": inventory_records,
    }
    return (
        "Analyze the following SQL-extracted demand planning KPIs and produce an S&OP "
        "executive summary with concrete inventory rebalancing recommendations:\n\n"
        f"{json.dumps(payload, indent=2)}"
    )