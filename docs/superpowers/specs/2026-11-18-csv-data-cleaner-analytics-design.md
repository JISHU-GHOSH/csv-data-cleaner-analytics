# Design Document: CSV Data Cleaner & Analytics Studio (Tkinter Desktop Application)

**Date:** 2026-11-18  
**Scope:** Architectural (New Desktop Application)  
**Target Environment:** Python 3.8+ on Windows / macOS / Linux  
**Primary Dependencies:** Python Standard Library (`tkinter`, `csv`, `os`, `sys`), `pandas`, `numpy`, `matplotlib`

---

## 1. Problem Statement & Goals

### 1.1 Problem Statement
Raw tabular data collected from forms, web scrapes, sensors, or school/business records frequently contains defects:
- Inconsistent and dirty column names (extra whitespace, mixed casing, special characters).
- Duplicate rows caused by multiple submissions or data collation errors.
- Missing (null/NaN) values in critical numeric and categorical columns.
- Unwanted leading/trailing whitespace in string fields.

Beginners and non-programmers often struggle to fix these issues programmatically. In college practicals and introductory data science settings, there is a strong demand for a standalone desktop software that clearly illustrates:
1. Identifying flaws in raw datasets ("Before" state).
2. Applying targeted data cleaning operations interactively ("Transformation").
3. Inspecting the resulting clean dataset alongside summary statistics and graphical visualizations ("After" state).
4. Exporting the cleaned dataset and a comprehensive change audit trail.

### 1.2 Core Goals
- **Interactive Tkinter Desktop GUI:** A professional, responsive desktop window with tabbed views, scrollable data table (`ttk.Treeview`), and action panels.
- **Before-and-After Demonstration:** Visual indicators showing real-time dataset health (duplicate counts, missing value counts, header validity) transitioning from warning (orange/red) to healthy (green).
- **Core Cleaning Engine:** Clean, tested data manipulation methods using Pandas for header normalization, duplicate removal, missing value imputation/deletion, and text trimming.
- **Statistical Analytics & EDA:** Calculation of descriptive statistics (mean, median, standard deviation, min, max, quartiles) for numeric fields, and frequency distributions for categorical fields.
- **Embedded Visualization:** Matplotlib plots (histograms, bar charts, boxplots) rendered directly inside a dedicated GUI tab via `FigureCanvasTkAgg`.
- **Audit Logging & Export:** Exporting cleaned CSV files and human-readable audit text reports detailing every cleaning action executed.
- **Zero-Crash Fault Tolerance:** Graceful error handling for missing files, invalid formats, non-numeric column selections, and corrupt entries.

---

## 2. System Architecture & Directory Structure

```
c:\python project\
├── data/
│   ├── sample_students_dirty.csv  # Pre-bundled messy student exam dataset
│   └── sample_sales_dirty.csv     # Pre-bundled commercial sales dataset
├── core/
│   ├── __init__.py
│   ├── data_manager.py            # Active & original DataFrame state management
│   ├── cleaner.py                 # Pure data transformation & cleaning functions
│   ├── stats_engine.py            # Summary statistics & frequency metrics
│   ├── audit_logger.py            # In-memory changelog and audit report formatter
│   └── exporter.py                # Disk I/O: CSV export & audit text export
├── gui/
│   ├── __init__.py
│   ├── app.py                     # Main window, layout grid, menu/toolbar, events
│   ├── table_view.py              # Scrollable spreadsheet widget using ttk.Treeview
│   ├── analytics_view.py          # Summary statistics display & metrics cards
│   ├── chart_view.py              # Matplotlib canvas embedded via FigureCanvasTkAgg
│   └── dialogs.py                 # User prompt modal dialogs (column pickers, imputation choice)
├── tests/
│   ├── __init__.py
│   └── test_cleaner.py            # Unit tests for cleaner functions and edge cases
├── main.py                        # Application entry point
├── requirements.txt               # Dependencies
└── README.md                      # Project manual, architecture guide, and viva Q&A
```

---

## 3. Detailed Component Specifications

### 3.1 `core/data_manager.py` (State & Health Assessment)
Manages the lifecycle of datasets in memory:
- `raw_df`: Original unedited DataFrame captured immediately upon loading.
- `current_df`: Active DataFrame undergoing transformations.
- `file_path`: Path of the loaded file (or "Sample Dataset").
- **Methods:**
  - `load_csv(filepath: str) -> None`: Reads CSV using pandas with encoding fallback (`utf-8`, `latin1`).
  - `load_sample(sample_name: str) -> None`: Loads pre-packaged bundled sample dataset.
  - `reset_to_raw() -> None`: Reverts `current_df` back to a deep copy of `raw_df`.
  - `get_health_metrics() -> dict`:
    - `total_rows`: `len(df)`
    - `total_cols`: `len(df.columns)`
    - `duplicate_count`: `df.duplicated().sum()`
    - `total_missing_cells`: `df.isna().sum().sum()`
    - `missing_per_col`: `df.isna().sum().to_dict()`
    - `has_unclean_headers`: whether column names contain extra spaces or mixed capitalization.

### 3.2 `core/cleaner.py` (Transformation Engine)
Pure functional transformations operating on Pandas DataFrames:
- `standardize_headers(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]`:
  - Strips leading/trailing spaces from column names.
  - Converts names to lowercase.
  - Replaces spaces and special characters with single underscores.
- `remove_duplicates(df: pd.DataFrame) -> Tuple[pd.DataFrame, str, int]`:
  - Detects and drops all duplicate rows (`df.drop_duplicates()`).
  - Returns count of removed rows.
- `handle_missing(df: pd.DataFrame, column: str, strategy: str, custom_val=None) -> Tuple[pd.DataFrame, str]`:
  - `strategy = "mean"`: Fills numeric NaN with column mean.
  - `strategy = "median"`: Fills numeric NaN with column median.
  - `strategy = "mode"`: Fills NaN with most frequent value.
  - `strategy = "custom"`: Fills NaN with `custom_val`.
  - `strategy = "drop_rows"`: Drops rows where the specified column (or any column) is NaN.
- `trim_whitespace(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]`:
  - Applies `.str.strip()` across all string/object columns.

### 3.3 `core/stats_engine.py` (Analytics Engine)
- `get_numeric_summary(df: pd.DataFrame) -> pd.DataFrame`:
  - Computes `count`, `mean`, `std`, `min`, `25%`, `50%` (median), `75%`, `max` for numeric columns.
- `get_categorical_summary(df: pd.DataFrame, column: str) -> pd.Series`:
  - Computes value counts and percentages for categorical fields.
- `get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame`:
  - Computes Pearson correlation matrix for numeric features.

### 3.4 `core/audit_logger.py` & `core/exporter.py`
- `AuditLogger`:
  - Tracks timestamp, action type, description, and rows affected.
  - Generates a formatted text summary for export and GUI display.
- `Exporter`:
  - `save_csv(df: pd.DataFrame, output_path: str) -> None`: Exports clean CSV with UTF-8 encoding.
  - `save_report(report_text: str, output_path: str) -> None`: Saves the audit log text file.

### 3.5 `gui/` (User Interface Modules)
- **`app.py`:** Root window (`tk.Tk`) configured with a clean modern `ttk` theme, a top toolbar (Load, Sample, Reset, Save), a two-column main frame (Tabs on Left, Action Panel on Right), and a bottom status bar.
- **`table_view.py`:** Uses `ttk.Treeview` with synchronized vertical & horizontal scrollbars. Features automatic column generation, formatted headers, and displays up to the first 500 rows for smooth scrolling performance.
- **`analytics_view.py`:** Tab showing statistical tables rendered in a read-only monospace scrolled text view or treeview.
- **`chart_view.py`:** Integrates `matplotlib.figure.Figure` with `FigureCanvasTkAgg`. Includes dropdown controls to select column, chart type (Histogram, Bar Chart, Boxplot), and a "Render Chart" button.
- **`dialogs.py`:** Custom Tkinter Toplevel dialogs for:
  - Missing value strategy selection (drop vs mean/median/mode).
  - Confirmation modals with action previews.

---

## 4. Pre-Packaged Demo Datasets

### 4.1 `sample_students_dirty.csv`
Contains 25 rows with realistic data flaws:
- Header issues: `"  Student ID "`, `" Full Name  "`, `"Age "`, `"  DEPARTMENT "`, `"Marks "`, `"Attendance % "`
- Missing values: Empty marks, missing age, missing department.
- Duplicates: 3 exact duplicate student rows.
- Whitespace flaws: `"  Computer Science  "`, `" IT"`.

### 4.2 `sample_sales_dirty.csv`
Commercial dataset with 30 rows containing missing sales figures, duplicate transactions, and negative anomaly values.

---

## 5. Error Handling & Edge Cases
- **Non-CSV or Corrupt File:** `pd.errors.ParserError` caught; displays error dialog: *"Invalid CSV file format."*
- **Empty File:** `pd.errors.EmptyDataError` caught; displays warning: *"The selected file contains no data."*
- **No File Loaded:** Action buttons check `if data_manager.has_data()`; if not, alerts user: *"Please load a dataset first."*
- **Non-Numeric Selection in Numeric Operations:** When calculating mean/median or plotting a histogram on a text column, the app prevents crashing and warns: *"Selected column is not numeric. Please choose a numeric column or generate a Bar Chart."*
- **Zero Division / Single Value Columns:** Handled gracefully in standard deviation and correlation computations.

---

## 6. Testing Strategy
- Unit test suite in `tests/test_cleaner.py` using standard `unittest`:
  - `test_standardize_headers`: Verifies whitespace trimming, lowercase conversion, and underscore replacement.
  - `test_remove_duplicates`: Confirms duplicate row count reduction and preservation of unique rows.
  - `test_handle_missing_mean_median`: Verifies numerical imputation calculates accurate values and replaces NaNs.
  - `test_handle_missing_drop`: Verifies row count reduction when dropping null rows.
  - `test_trim_whitespace`: Verifies text columns are stripped of spaces.

---

## 7. Viva Q&A & Educational Highlights
The project comes with a comprehensive `README.md` containing:
- Installation & setup instructions.
- Architecture diagram and file breakdown.
- 10 common viva questions with concise model answers covering:
  - Why Pandas is used over native lists/dictionaries for tabular data.
  - Mean vs Median imputation (when to use which based on skewness/outliers).
  - How `ttk.Treeview` and `FigureCanvasTkAgg` work in Tkinter.
  - The importance of keeping an immutable copy of raw data for reset/audit.
