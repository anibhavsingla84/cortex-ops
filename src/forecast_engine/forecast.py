
import pandas as pd
import numpy as np

def forecast_cashflows(df, months=12, cpr=0.02, cdr=0.01, recovery_lag=6, recovery_rate=0.2):
    forecasts = []
    for _, loan in df.iterrows():
        principal = loan.get("current_principal_balance", 0)
        rate = loan.get("interest_rate", 0) / 12
        monthly_payment = loan.get("monthly_payment", principal * rate)
        orig_balance = principal

        status = loan.get("loan_status", "current")
        loan_id = loan.get("loan_id", "unknown")

        for m in range(1, months + 1):
            interest = principal * rate
            principal_payment = max(0, monthly_payment - interest)
            default_amount = 0
            recovery = 0

            if status == "charged_off":
                forecasts.append({
                    "loan_id": loan_id,
                    "month": m,
                    "principal": 0,
                    "interest": 0,
                    "default": 0,
                    "recovery": 0,
                    "ending_balance": 0
                })
                break

            if m > 2 and np.random.rand() < cdr:
                default_amount = principal
                status = "charged_off"
                principal = 0

            elif np.random.rand() < cpr:
                principal_payment = principal
                principal = 0

            else:
                principal = max(0, principal - principal_payment)

            if m == recovery_lag and default_amount > 0:
                recovery = default_amount * recovery_rate

            forecasts.append({
                "loan_id": loan_id,
                "month": m,
                "principal": principal_payment,
                "interest": interest,
                "default": default_amount,
                "recovery": recovery,
                "ending_balance": principal,
                "orig_balance": orig_balance
            })

            if principal <= 0:
                break

    forecast_df = pd.DataFrame(forecasts)

    # Cohort-level metrics
    summary = forecast_df.groupby("month").agg({
        "principal": "sum",
        "interest": "sum",
        "default": "sum",
        "recovery": "sum",
        "orig_balance": "sum"
    }).reset_index()

    summary["net_cashflow"] = summary["principal"] + summary["interest"] + summary["recovery"] - summary["default"]
    irr = np.irr(summary["net_cashflow"].values)
    nim = summary["interest"].sum() / summary["orig_balance"].sum() if summary["orig_balance"].sum() > 0 else 0

    return forecast_df, irr, nim
