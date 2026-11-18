"""Data Manager module.

Manages the lifecycle of datasets, including loading, backup/reset,
and health metrics calculation.
"""

from typing import Tuple, Dict, Any, Optional
import os
import pandas as pd


class DataManager:
    """Manages active dataset, immutable raw backup, and health metrics."""

    def __init__(self) -> None:
        self.raw_df: Optional[pd.DataFrame] = None
        self.current_df: Optional[pd.DataFrame] = None
        self.source_name: str = ""

    def has_data(self) -> bool:
        """Returns True if a valid DataFrame is currently loaded."""
        return self.current_df is not None and not self.current_df.empty

    def load_csv(self, filepath: str) -> Tuple[bool, str]:
        """Loads a CSV file from disk with encoding fallback."""
        if not os.path.exists(filepath):
            return False, f"File not found: {filepath}"

        encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1"]
        last_error = ""

        for enc in encodings:
            try:
                df = pd.read_csv(filepath, encoding=enc)
                if df.empty:
                    return False, "The selected CSV file is empty."

                self.raw_df = df.copy(deep=True)
                self.current_df = df.copy(deep=True)
                self.source_name = os.path.basename(filepath)
                return True, f"Loaded {self.source_name} successfully ({len(df)} rows, {len(df.columns)} columns)."
            except Exception as e:
                last_error = str(e)
                continue

        return False, f"Failed to read CSV: {last_error}"

    def load_sample(self, sample_key: str = "students") -> Tuple[bool, str]:
        """Loads one of the pre-bundled sample datasets."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if sample_key == "sales":
            path = os.path.join(base_dir, "data", "sample_sales_dirty.csv")
        else:
            path = os.path.join(base_dir, "data", "sample_students_dirty.csv")

        return self.load_csv(path)

    def reset_to_raw(self) -> Tuple[bool, str]:
        """Restores the current DataFrame back to the original loaded snapshot."""
        if self.raw_df is None:
            return False, "No original dataset to restore."

        self.current_df = self.raw_df.copy(deep=True)
        return True, "Dataset restored to original loaded state."

    def get_health_metrics(self) -> Dict[str, Any]:
        """Calculates comprehensive health indicators for the active dataset."""
        if not self.has_data() or self.current_df is None:
            return {
                "total_rows": 0,
                "total_cols": 0,
                "duplicate_count": 0,
                "total_missing_cells": 0,
                "missing_per_col": {},
                "has_unclean_headers": False,
                "columns": [],
                "dtypes": {},
            }

        df = self.current_df
        total_rows = len(df)
        total_cols = len(df.columns)
        duplicate_count = int(df.duplicated().sum())
        missing_per_col = df.isna().sum().to_dict()
        total_missing_cells = int(df.isna().sum().sum())

        # Check for unclean headers: leading/trailing whitespace, uppercase, or special chars
        has_unclean_headers = any(
            col != col.strip().lower().replace(" ", "_") for col in df.columns
        )

        return {
            "total_rows": total_rows,
            "total_cols": total_cols,
            "duplicate_count": duplicate_count,
            "total_missing_cells": total_missing_cells,
            "missing_per_col": missing_per_col,
            "has_unclean_headers": has_unclean_headers,
            "columns": list(df.columns),
            "dtypes": {str(k): str(v) for k, v in df.dtypes.to_dict().items()},
        }
