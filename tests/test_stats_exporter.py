import unittest
import os
import shutil
import tempfile
import pandas as pd
from core.stats_engine import (
    get_numeric_summary,
    get_categorical_summary,
    get_correlation_matrix,
)
from core.audit_logger import AuditLogger
from core.exporter import save_csv, save_report

class TestStatsAndExporter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.df = pd.DataFrame({
            "age": [20, 22, 24, 26, 28],
            "score": [80.0, 85.0, 90.0, 95.0, 100.0],
            "dept": ["CS", "IT", "CS", "CS", "IT"],
        })

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_numeric_summary(self):
        summary = get_numeric_summary(self.df)
        self.assertIn("age", summary.columns)
        self.assertIn("score", summary.columns)
        self.assertNotIn("dept", summary.columns)
        self.assertIn("mean", summary.index)
        self.assertEqual(summary.loc["mean", "age"], 24.0)

    def test_categorical_summary(self):
        summary = get_categorical_summary(self.df, "dept")
        self.assertIn("count", summary.columns)
        self.assertIn("percentage", summary.columns)
        self.assertEqual(summary.loc["CS", "count"], 3)

    def test_correlation_matrix(self):
        corr = get_correlation_matrix(self.df)
        self.assertAlmostEqual(corr.loc["age", "score"], 1.0)

    def test_audit_logger(self):
        logger = AuditLogger()
        self.assertEqual(len(logger.get_logs()), 0)
        logger.log("Deduplication", "Removed 3 duplicate rows.")
        logger.log("Missing Values", "Filled missing score with mean 85.0.")
        self.assertEqual(len(logger.get_logs()), 2)
        report = logger.get_report_text()
        self.assertIn("Deduplication", report)
        self.assertIn("Removed 3 duplicate rows.", report)

    def test_save_csv(self):
        out_path = os.path.join(self.test_dir, "clean.csv")
        success, msg = save_csv(self.df, out_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_path))
        loaded = pd.read_csv(out_path)
        self.assertEqual(len(loaded), 5)

    def test_save_report(self):
        out_path = os.path.join(self.test_dir, "report.txt")
        success, msg = save_report("Sample Audit Report Content", out_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_path))
        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, "Sample Audit Report Content")

if __name__ == "__main__":
    unittest.main()
