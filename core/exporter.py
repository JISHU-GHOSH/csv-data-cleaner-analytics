"""Exporter module.

Handles safe writing of cleaned datasets to CSV and audit reports to text files.
"""

from typing import Tuple
import os
import pandas as pd


def save_csv(df: pd.DataFrame, output_path: str) -> Tuple[bool, str]:
    """Saves a pandas DataFrame to CSV with UTF-8 encoding."""
    try:
        dirname = os.path.dirname(output_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        df.to_csv(output_path, index=False, encoding="utf-8")
        return True, f"Saved cleaned CSV to {output_path} ({len(df)} rows)."
    except Exception as e:
        return False, f"Failed to save CSV: {str(e)}"


def save_report(report_text: str, output_path: str) -> Tuple[bool, str]:
    """Writes audit report text to a file."""
    try:
        dirname = os.path.dirname(output_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        return True, f"Saved audit report to {output_path}."
    except Exception as e:
        return False, f"Failed to save report: {str(e)}"
