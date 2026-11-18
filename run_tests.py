"""Automated Test Runner for CSV Data Cleaner & Analytics Studio.

Executes all unit tests and outputs a structured summary report.
"""

import sys
import unittest


def run_all_tests() -> int:
    """Discovers and runs all unit tests in the tests/ directory."""
    print("=" * 70)
    print("   CSV DATA CLEANER & ANALYTICS STUDIO — UNIT TEST SUITE")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 70)
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors

    print(f"Results: {total} run | {passed} passed | {failures} failed | {errors} errors")

    if result.wasSuccessful():
        print("ALL TESTS PASSED! Project is viva-ready.")
        print("=" * 70)
        return 0
    else:
        print("SOME TESTS FAILED. Please review the tracebacks above.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
