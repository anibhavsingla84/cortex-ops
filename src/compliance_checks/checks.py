
def check_concentration_limits(df, limit_ratio=0.25):
    result = df.groupby('state')['loan_id'].count().div(len(df))
    breaches = result[result > limit_ratio]
    return breaches
