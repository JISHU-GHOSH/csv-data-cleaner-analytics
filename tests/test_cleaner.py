import unittest
import pandas as pd
import numpy as np
from core.cleaner import (
    standardize_headers,
    remove_duplicates,
    handle_missing,
    trim_whitespace,
    auto_clean_all,
)

class TestCleaner(unittest.TestCase):
    def setUp(self):
        self.dirty_df = pd.DataFrame({
            "  Full Name ": [" Alice ", "Bob", " Alice ", "  Charlie  ", None],
            "Age ": [20.0, np.nan, 20.0, 24.0, 22.0],
            " SCORE ": [85.0, 90.0, 85.0, np.nan, 70.0],
            "Department": ["  CS ", "IT", "  CS ", "CS", "IT"],
        })

    def test_standardize_headers(self):
        clean_df, msg = standardize_headers(self.dirty_df)
        expected_cols = ["full_name", "age", "score", "department"]
        self.assertEqual(list(clean_df.columns), expected_cols)
        self.assertIn("Standardized", msg)

    def test_remove_duplicates(self):
        clean_df, msg, count = remove_duplicates(self.dirty_df)
        self.assertEqual(count, 1)
        self.assertEqual(len(clean_df), 4)

    def test_trim_whitespace(self):
        clean_df, msg = trim_whitespace(self.dirty_df)
        self.assertEqual(clean_df.iloc[0]["  Full Name "], "Alice")
        self.assertEqual(clean_df.iloc[3]["  Full Name "], "Charlie")
        self.assertEqual(clean_df.iloc[0]["Department"], "CS")

    def test_handle_missing_mean(self):
        clean_df, msg = handle_missing(self.dirty_df, column="Age ", strategy="mean")
        self.assertFalse(clean_df["Age "].isna().any())
        self.assertAlmostEqual(clean_df.iloc[1]["Age "], 21.5)

    def test_handle_missing_median(self):
        clean_df, msg = handle_missing(self.dirty_df, column="Age ", strategy="median")
        self.assertFalse(clean_df["Age "].isna().any())
        self.assertAlmostEqual(clean_df.iloc[1]["Age "], 21.0)

    def test_handle_missing_mode(self):
        clean_df, msg = handle_missing(self.dirty_df, column="Department", strategy="mode")
        self.assertFalse(clean_df["Department"].isna().any())

    def test_handle_missing_drop_rows(self):
        clean_df, msg = handle_missing(self.dirty_df, column="Age ", strategy="drop_rows")
        self.assertEqual(len(clean_df), 4)
        self.assertFalse(clean_df["Age "].isna().any())

    def test_handle_missing_custom(self):
        clean_df, msg = handle_missing(self.dirty_df, column="  Full Name ", strategy="custom", custom_val="Unknown")
        self.assertEqual(clean_df.iloc[4]["  Full Name "], "Unknown")

    def test_auto_clean_all(self):
        clean_df, log = auto_clean_all(self.dirty_df)
        self.assertEqual(clean_df.isna().sum().sum(), 0)
        self.assertFalse(clean_df.duplicated().any())
        self.assertEqual(list(clean_df.columns), ["full_name", "age", "score", "department"])
        self.assertGreater(len(log), 0)

if __name__ == "__main__":
    unittest.main()
