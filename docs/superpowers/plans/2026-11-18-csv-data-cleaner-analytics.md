# CSV Data Cleaner & Analytics Studio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a robust, modular Tkinter desktop application with Pandas, NumPy, and Matplotlib that allows students to inspect raw dirty CSV datasets, perform one-click cleaning transformations (deduplication, missing value handling, header normalization), view statistical summaries and embedded charts, and export clean data with an audit trail.

**Architecture:** Layered architecture separating the pure data processing engine (`core/`) from the presentation layer (`gui/`). The `core/` package handles dataset loading, health diagnostics, pure transformations, statistical aggregations, and audit logging. The `gui/` package provides a Tkinter notebook interface with a spreadsheet table (`ttk.Treeview`), embedded Matplotlib figures (`FigureCanvasTkAgg`), health status badges, and action dialogs.

**Tech Stack:** Python 3.8+, `tkinter`, `ttk`, `pandas`, `numpy`, `matplotlib`, `unittest`.

**Spec:** [docs/superpowers/specs/2026-11-18-csv-data-cleaner-analytics-design.md](file:///c:/python%20project/docs/superpowers/specs/2026-11-18-csv-data-cleaner-analytics-design.md)

## Global Constraints

- Must run on standard Python with `pandas`, `numpy`, `matplotlib`, and built-in `tkinter`.
- Zero-crash guarantee: all file I/O and user interactions must be protected with `try...except` and informative dialogs.
- Preserve raw data snapshot at all times to allow instant "Reset to Original" functionality.
- TDD required: core transformations must have automated tests using Python's standard `unittest`.

---

### Task 1: Environment Setup & Demo Dirty Datasets

**Files:**
- Create: `requirements.txt`
- Create: `data/sample_students_dirty.csv`
- Create: `data/sample_sales_dirty.csv`

**Interfaces:**
- Produces: `requirements.txt` with dependencies (`pandas`, `numpy`, `matplotlib`), and two realistic CSV datasets containing deliberate duplicates, whitespace defects, and missing values.

- [ ] **Step 1: Create `requirements.txt`**
- [ ] **Step 2: Create `data/sample_students_dirty.csv` with 25 rows, dirty headers, missing marks, and duplicates**
- [ ] **Step 3: Create `data/sample_sales_dirty.csv` with sales transaction data and anomalies**
- [ ] **Step 4: Verify files are readable by pandas in python**
- [ ] **Step 5: Git commit task deliverables**

---

### Task 2: Core Data Manager & Health Inspector

**Files:**
- Create: `core/__init__.py`
- Create: `core/data_manager.py`
- Create: `tests/__init__.py`
- Create: `tests/test_data_manager.py`

**Interfaces:**
- Produces: `DataManager` class with methods:
  - `load_csv(filepath: str) -> Tuple[bool, str]`
  - `load_sample(sample_key: str) -> Tuple[bool, str]`
  - `reset_to_raw() -> None`
  - `get_health_metrics() -> dict` (total rows, cols, duplicate count, missing cell count, missing per col)
  - `has_data() -> bool`

- [ ] **Step 1: Write failing unit test in `tests/test_data_manager.py`**
- [ ] **Step 2: Run test and observe failure**
- [ ] **Step 3: Implement `core/data_manager.py`**
- [ ] **Step 4: Run tests and ensure 100% pass**
- [ ] **Step 5: Git commit task deliverables**

---

### Task 3: Core Cleaner Engine (TDD)

**Files:**
- Create: `core/cleaner.py`
- Create: `tests/test_cleaner.py`

**Interfaces:**
- Consumes: `pandas.DataFrame`
- Produces:
  - `standardize_headers(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]`
  - `remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, str, int]`
  - `handle_missing(df: pd.DataFrame, column: str, strategy: str, custom_val=None) -> Tuple[pd.DataFrame, str]`
  - `trim_whitespace(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]`

- [ ] **Step 1: Write comprehensive failing tests in `tests/test_cleaner.py`**
- [ ] **Step 2: Run tests and confirm failures**
- [ ] **Step 3: Implement `core/cleaner.py`**
- [ ] **Step 4: Run tests and verify all pass**
- [ ] **Step 5: Git commit task deliverables**

---

### Task 4: Analytics Engine, Audit Logger & Exporter

**Files:**
- Create: `core/stats_engine.py`
- Create: `core/audit_logger.py`
- Create: `core/exporter.py`
- Create: `tests/test_stats_exporter.py`

**Interfaces:**
- Produces:
  - `get_numeric_summary(df) -> pd.DataFrame`
  - `get_categorical_summary(df, col) -> pd.Series`
  - `AuditLogger`: `log(action, details)`, `get_logs()`, `get_report_text()`, `clear()`
  - `Exporter`: `save_csv(df, path)`, `save_report(text, path)`

- [ ] **Step 1: Write failing tests in `tests/test_stats_exporter.py`**
- [ ] **Step 2: Run test and verify failure**
- [ ] **Step 3: Implement `stats_engine.py`, `audit_logger.py`, and `exporter.py`**
- [ ] **Step 4: Run test suite to verify passing**
- [ ] **Step 5: Git commit task deliverables**

---

### Task 5: GUI Table View & Custom Dialogs

**Files:**
- Create: `gui/__init__.py`
- Create: `gui/table_view.py`
- Create: `gui/dialogs.py`

**Interfaces:**
- Produces:
  - `TableView(parent)`: `update_data(df: pd.DataFrame)`, `clear()`
  - `show_missing_value_dialog(parent, columns)`: prompts for column & strategy (mean, median, mode, custom, drop)
  - `show_column_picker_dialog(parent, columns, title)`: prompts for column selection

- [ ] **Step 1: Implement `gui/table_view.py` with `ttk.Treeview` and scrollbars**
- [ ] **Step 2: Implement `gui/dialogs.py` for user input modals**
- [ ] **Step 3: Verify dialog and table widgets initialize cleanly**
- [ ] **Step 4: Git commit task deliverables**

---

### Task 6: GUI Analytics View & Embedded Chart View

**Files:**
- Create: `gui/analytics_view.py`
- Create: `gui/chart_view.py`

**Interfaces:**
- Produces:
  - `AnalyticsView(parent)`: `update_stats(df: pd.DataFrame)`
  - `ChartView(parent)`: `render_plot(df: pd.DataFrame, col: str, plot_type: str)`

- [ ] **Step 1: Implement `gui/analytics_view.py` with structured metrics display**
- [ ] **Step 2: Implement `gui/chart_view.py` embedding `FigureCanvasTkAgg`**
- [ ] **Step 3: Verify chart view handles histograms, bar charts, and boxplots without error**
- [ ] **Step 4: Git commit task deliverables**

---

### Task 7: Main GUI Integration & Entry Point

**Files:**
- Create: `gui/app.py`
- Create: `main.py`

**Interfaces:**
- Consumes: All `core/` and `gui/` components
- Produces: Complete executable application launched via `python main.py`

- [ ] **Step 1: Implement `gui/app.py` integrating toolbar, sidebar, tabs, and status bar**
- [ ] **Step 2: Wire all cleaning buttons and data managers with responsive status updates**
- [ ] **Step 3: Implement `main.py` launcher**
- [ ] **Step 4: Run smoke test verifying app startup**
- [ ] **Step 5: Git commit task deliverables**

---

### Task 8: Verification, Test Runner & Comprehensive Viva Guide

**Files:**
- Create: `README.md`
- Create: `run_tests.py`

**Interfaces:**
- Produces:
  - One-click test runner `python run_tests.py`
  - Complete `README.md` with:
    - Step-by-step viva presentation walkthrough
    - 10 common viva questions & ready-to-answer explanations
    - Project architecture and code highlights

- [ ] **Step 1: Create `run_tests.py` to run all unit tests with formatted report**
- [ ] **Step 2: Execute full test suite and confirm all tests pass**
- [ ] **Step 3: Write comprehensive `README.md` with viva prep guide**
- [ ] **Step 4: Final git commit and tag**
