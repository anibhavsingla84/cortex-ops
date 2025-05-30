
import pandas as pd

def generate_lp_summary(df):
    summary = {
        "Total Loans": len(df),
        "Total Outstanding Balance": df["current_principal_balance"].sum(),
        "Average Interest Rate": df["interest_rate"].mean(),
        "Charge-off Rate": (df["loan_status"] == "charged_off").mean()
    }
    return pd.DataFrame(summary.items(), columns=["Metric", "Value"])
