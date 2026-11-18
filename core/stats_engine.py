import pandas as pd

def get_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=["number"]).columns
    if len(numeric_cols) == 0:
        return pd.DataFrame()

    summary = df[numeric_cols].describe().round(2)
    return summary

def get_categorical_summary(df: pd.DataFrame, column: str) -> pd.DataFrame:
    if column not in df.columns:
        return pd.DataFrame()

    counts = df[column].value_counts(dropna=False)
    percentages = (df[column].value_counts(normalize=True, dropna=False) * 100).round(2)

    result = pd.DataFrame({
        "count": counts,
        "percentage": percentages,
    })
    return result

def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=["number"]).columns
    if len(numeric_cols) < 2:
        return pd.DataFrame()

    corr = df[numeric_cols].corr().round(2)
    return corr
