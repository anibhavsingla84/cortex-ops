
import pandas as pd

def calculate_monthly_interest(principal, annual_rate):
    return principal * (annual_rate / 100) / 12

def apply_waterfall(df):
    df = df.copy()
    df['interest_due'] = df.apply(lambda row: calculate_monthly_interest(row['current_principal_balance'], row['interest_rate']), axis=1)
    df['principal_payment'] = df['monthly_payment'] - df['interest_due']
    df['principal_payment'] = df['principal_payment'].apply(lambda x: max(x, 0))
    df['new_balance'] = df['current_principal_balance'] - df['principal_payment']
    df['new_balance'] = df['new_balance'].apply(lambda x: max(x, 0))
    df['charged_off_flag'] = df.apply(lambda row: 1 if row['loan_status'] == 'charged_off' else 0, axis=1)
    return df[['loan_id', 'current_principal_balance', 'interest_due', 'principal_payment', 'new_balance', 'charged_off_flag']]
