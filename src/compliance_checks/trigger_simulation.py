
import pandas as pd

def check_trigger_breaches(forecast_df, advance_rate=0.85, threshold_60dpd=0.05):
    # Group by month to simulate future triggers
    grouped = forecast_df.groupby("month").agg({
        "principal": "sum",
        "interest": "sum",
        "default": "sum",
        "ending_balance": "sum"
    }).reset_index()

    # Simulate a proxy for 60+ DPD from cumulative defaults
    grouped["cumulative_defaults"] = grouped["default"].cumsum()
    grouped["default_rate"] = grouped["cumulative_defaults"] / grouped["ending_balance"].replace(0, 1)

    # Eligibility-based test (advance rate)
    grouped["eligible_balance"] = grouped["ending_balance"] * advance_rate
    grouped["excess_principal"] = grouped["ending_balance"] - grouped["eligible_balance"]

    # Trigger breach flags
    grouped["trigger_breach_default"] = grouped["default_rate"] > threshold_60dpd
    grouped["trigger_breach_haircut"] = grouped["excess_principal"] < 0

    return grouped[["month", "ending_balance", "default_rate", "excess_principal", "trigger_breach_default", "trigger_breach_haircut"]]
