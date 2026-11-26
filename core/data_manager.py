import os
from typing import Tuple, Dict, Any, Optional, List
import pandas as pd

class DataManager:
    def __init__(self):
        self.raw_df: Optional[pd.DataFrame] = None
        self.current_df: Optional[pd.DataFrame] = None
        self.source_name: str = ""
        self.history: List[pd.DataFrame] = []

    def has_data(self) -> bool:
        return self.current_df is not None and not self.current_df.empty

    def push_history(self) -> None:
        if self.current_df is not None:
            self.history.append(self.current_df.copy(deep=True))
            if len(self.history) > 15:
                self.history.pop(0)

    def undo(self) -> Tuple[bool, str]:
        if not self.history:
            return False, "Nothing to undo."
        self.current_df = self.history.pop()
        return True, "Reverted to previous state."

    def load_csv(self, filepath: str) -> Tuple[bool, str]:
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
                self.history.clear()
                return True, f"Loaded {self.source_name} successfully ({len(df)} rows, {len(df.columns)} columns)."
            except Exception as e:
                last_error = str(e)
                continue

        return False, f"Failed to read CSV: {last_error}"

    def load_sample(self, sample_key: str = "students") -> Tuple[bool, str]:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if sample_key == "sales":
            path = os.path.join(base_dir, "data", "sample_sales_dirty.csv")
        else:
            path = os.path.join(base_dir, "data", "sample_students_dirty.csv")

        return self.load_csv(path)

    def reset_to_raw(self) -> Tuple[bool, str]:
        if self.raw_df is None:
            return False, "No original dataset to restore."

        self.push_history()
        self.current_df = self.raw_df.copy(deep=True)
        return True, "Dataset restored to original loaded state."

    def get_quality_score(self) -> int:
        if not self.has_data() or self.current_df is None:
            return 0
        df = self.current_df
        total_cells = df.size
        if total_cells == 0:
            return 0
        missing_cells = df.isna().sum().sum()
        completeness = max(0.0, 1.0 - (missing_cells / total_cells))

        dup_rows = df.duplicated().sum()
        uniqueness = max(0.0, 1.0 - (dup_rows / len(df))) if len(df) > 0 else 1.0

        has_unclean = any(col != col.strip().lower().replace(" ", "_") for col in df.columns)
        header_score = 0.8 if has_unclean else 1.0

        score = int((completeness * 0.5 + uniqueness * 0.3 + header_score * 0.2) * 100)
        return min(100, max(0, score))

    def get_health_metrics(self) -> Dict[str, Any]:
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
                "quality_score": 0,
                "can_undo": False,
            }

        df = self.current_df
        total_rows = len(df)
        total_cols = len(df.columns)
        duplicate_count = int(df.duplicated().sum())
        missing_per_col = df.isna().sum().to_dict()
        total_missing_cells = int(df.isna().sum().sum())

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
            "quality_score": self.get_quality_score(),
            "can_undo": len(self.history) > 0,
        }
