import unittest
import os
import pandas as pd
from core.data_manager import DataManager

class TestDataManager(unittest.TestCase):
    def setUp(self):
        self.dm = DataManager()
        self.sample_path = os.path.join("data", "sample_students_dirty.csv")

    def test_initial_state(self):
        self.assertFalse(self.dm.has_data())
        self.assertIsNone(self.dm.current_df)
        self.assertIsNone(self.dm.raw_df)

    def test_load_csv_success(self):
        success, msg = self.dm.load_csv(self.sample_path)
        self.assertTrue(success)
        self.assertTrue(self.dm.has_data())
        self.assertEqual(len(self.dm.current_df), 25)
        self.assertIn("Loaded", msg)

    def test_load_csv_nonexistent(self):
        success, msg = self.dm.load_csv("nonexistent_file.csv")
        self.assertFalse(success)
        self.assertFalse(self.dm.has_data())

    def test_health_metrics(self):
        self.dm.load_csv(self.sample_path)
        metrics = self.dm.get_health_metrics()
        self.assertEqual(metrics["total_rows"], 25)
        self.assertEqual(metrics["total_cols"], 6)
        self.assertGreater(metrics["duplicate_count"], 0)
        self.assertGreater(metrics["total_missing_cells"], 0)
        self.assertTrue(metrics["has_unclean_headers"])

    def test_reset_to_raw(self):
        self.dm.load_csv(self.sample_path)
        self.dm.current_df = self.dm.current_df.iloc[:5].copy()
        self.assertEqual(len(self.dm.current_df), 5)
        self.dm.reset_to_raw()
        self.assertEqual(len(self.dm.current_df), 25)

    def test_undo(self):
        self.dm.load_csv(self.sample_path)
        self.dm.push_history()
        self.dm.current_df = self.dm.current_df.iloc[:10].copy()
        self.assertEqual(len(self.dm.current_df), 10)
        success, msg = self.dm.undo()
        self.assertTrue(success)
        self.assertEqual(len(self.dm.current_df), 25)

    def test_quality_score(self):
        self.dm.load_csv(self.sample_path)
        score = self.dm.get_quality_score()
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

if __name__ == "__main__":
    unittest.main()
