"""Cleaner module.

Provides pure functions for cleaning and standardizing pandas DataFrames:
- Column header normalization
- Deduplication
- Missing value imputation/deletion
- String whitespace trimming
- Automated all-in-one cleaning pipeline
"""

import re
from typing import Tuple, List, Any, Optional
import pandas as pd
import numpy as np


def standardize_headers(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """Standardizes column names by stripping spaces, lowercasing,

    and replacing special characters and multiple spaces with underscores.
    """
    new_df = df.copy()
    old_cols = list(new_df.columns)
    new_cols = []

    for col in old_cols:
        cleaned = str(col).strip().lower()
        # Replace non-alphanumeric (except underscore) with underscore
        cleaned = re.sub(r"[^\w\s]", "", cleaned)
        cleaned = re.sub(r"[\s_]+", "_", cleaned).strip("_")
        new_cols.append(cleaned)

    # Ensure unique column names if collisions happen
    seen = {}
    deduped_cols = []
    for col in new_cols:
        if col in seen:
            seen[col] += 1
            deduped_cols.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            deduped_cols.append(col)

    new_df.columns = deduped_cols
    return new_df, f"Standardized {len(new_cols)} column headers."


def remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, str, int]:
    """Identifies and drops all duplicate rows in the DataFrame."""
    new_df = df.copy()
    initial_rows = len(new_df)
    new_df = new_df.drop_duplicates().reset_index(drop=True)
    removed_count = initial_rows - len(new_df)

    if removed_count > 0:
        msg = f"Removed {removed_count} duplicate row(s)."
    else:
        msg = "No duplicate rows found."

    return new_df, msg, removed_count


def trim_whitespace(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """Strips leading and trailing whitespace from all string/object columns."""
    new_df = df.copy()
    trimmed_cols = 0

    for col in new_df.columns:
        if pd.api.types.is_string_dtype(new_df[col]) or pd.api.types.is_object_dtype(new_df[col]):
            # Apply str.strip to non-null string entries
            new_df[col] = new_df[col].apply(
                lambda x: x.strip() if isinstance(x, str) else x
            )
            trimmed_cols += 1

    return new_df, f"Trimmed whitespace in {trimmed_cols} text column(s)."


def handle_missing(
    df: pd.DataFrame,
    column: str,
    strategy: str,
    custom_val: Optional[Any] = None,
) -> Tuple[pd.DataFrame, str]:
    """Handles missing (NaN/None) values in a given column or across all columns.

    Strategies supported:
    - 'mean': Fills numeric NaNs with the column mean.
    - 'median': Fills numeric NaNs with the column median.
    - 'mode': Fills NaNs with the most frequent value.
    - 'custom': Fills NaNs with a user-provided value.
    - 'drop_rows': Drops rows where the column is null (or any row if column == 'all').
    """
    new_df = df.copy()

    if column != "all" and column not in new_df.columns:
        return new_df, f"Column '{column}' does not exist."

    if strategy == "drop_rows":
        initial_count = len(new_df)
        if column == "all":
            new_df = new_df.dropna().reset_index(drop=True)
        else:
            new_df = new_df.dropna(subset=[column]).reset_index(drop=True)
        dropped = initial_count - len(new_df)
        return new_df, f"Dropped {dropped} row(s) containing missing values."

    target_cols = new_df.columns if column == "all" else [column]

    for col in target_cols:
        col_series = new_df[col]
        missing_count = col_series.isna().sum()
        if missing_count == 0:
            continue

        if strategy == "mean":
            if pd.api.types.is_numeric_dtype(col_series):
                fill_val = col_series.mean()
                new_df[col] = col_series.fillna(fill_val)
            else:
                return new_df, f"Cannot compute mean for non-numeric column '{col}'."

        elif strategy == "median":
            if pd.api.types.is_numeric_dtype(col_series):
                fill_val = col_series.median()
                new_df[col] = col_series.fillna(fill_val)
            else:
                return new_df, f"Cannot compute median for non-numeric column '{col}'."

        elif strategy == "mode":
            mode_vals = col_series.mode()
            if not mode_vals.empty:
                fill_val = mode_vals.iloc[0]
                new_df[col] = col_series.fillna(fill_val)

        elif strategy == "custom":
            # Attempt numeric conversion if original column is numeric
            val_to_use = custom_val
            if pd.api.types.is_numeric_dtype(col_series):
                try:
                    val_to_use = float(custom_val)
                except (ValueError, TypeError):
                    pass
            new_df[col] = col_series.fillna(val_to_use)

        else:
            return new_df, f"Unknown missing value strategy: '{strategy}'."

    return new_df, f"Applied '{strategy}' missing value strategy to column '{column}'."


def auto_clean_all(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Runs a complete, sensible automated cleaning pipeline:

    1. Trim whitespace in text fields
    2. Standardize column headers
    3. Drop duplicate rows
    4. Impute missing numbers with median
    5. Impute missing text with mode (or 'Unknown')
    """
    logs = []
    current, msg = trim_whitespace(df)
    logs.append(msg)

    current, msg = standardize_headers(current)
    logs.append(msg)

    current, msg, _ = remove_duplicates(current)
    logs.append(msg)

    for col in current.columns:
        if current[col].isna().sum() > 0:
            if pd.api.types.is_numeric_dtype(current[col]):
                current, msg = handle_missing(current, col, strategy="median")
                logs.append(f"Filled missing numeric values in '{col}' with median.")
            else:
                mode_vals = current[col].mode()
                if not mode_vals.empty:
                    current, msg = handle_missing(current, col, strategy="mode")
                    logs.append(f"Filled missing text values in '{col}' with mode.")
                else:
                    current, msg = handle_missing(current, col, strategy="custom", custom_val="Unknown")
                    logs.append(f"Filled missing text values in '{col}' with 'Unknown'.")

    return current, logs
