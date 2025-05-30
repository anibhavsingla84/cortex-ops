
import pandas as pd

def segment_and_cohort_metrics(df, group_by=["vintage", "fico_bucket"]):
    # Create dummy fields if missing
    if "origination_date" not in df.columns:
        df["origination_date"] = pd.to_datetime("2023-01-01")
    if "fico_score" in df.columns:
        df["fico_bucket"] = pd.cut(df["fico_score"], bins=[0, 600, 660, 720, 780, 850], labels=["<600", "600-659", "660-719", "720-779", "780+"])
    else:
        df["fico_bucket"] = "unknown"

    if "loan_term_months" not in df.columns:
        df["loan_term_months"] = 36

    if "vintage" not in df.columns:
        df["vintage"] = df["origination_date"].dt.to_period("M")

    # Define key metrics
    metrics = df.groupby(group_by).agg(
        count_loans=("loan_id", "count"),
        total_balance=("current_principal_balance", "sum"),
        avg_apr=("interest_rate", "mean"),
        avg_term=("loan_term_months", "mean"),
        est_monthly_payment=("monthly_payment", "mean")
    ).reset_index()

    # IRR / NIM estimation placeholders
    metrics["projected_irr"] = (metrics["avg_apr"] * 0.8).round(4)  # Dummy proxy
    metrics["projected_nim"] = (metrics["avg_apr"] * 0.65).round(4)

    return metrics
