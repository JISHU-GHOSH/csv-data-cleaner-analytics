# 📊 CSV Data Cleaner & Analytics Studio
> **A Desktop Application for Automated Data Inspection, Cleaning, Statistical Analysis & Visualization in Python.**  
> Built for College End-Semester Practical Examinations and Viva Voce.

---

## 🚀 1. Overview
In real-world data science and software engineering, raw datasets collected from web forms, sensors, surveys, or legacy databases are rarely clean. They suffer from:
- Duplicate records
- Missing (NaN/null) values in key numerical and text fields
- Inconsistent and irregular column headers (e.g. `" Student Name "`, `"MARKS  "`)
- Whitespace contamination in text fields

**CSV Data Cleaner & Analytics Studio** is an interactive desktop GUI application built in Python using `tkinter`, `pandas`, `numpy`, and `matplotlib`. It provides an intuitive platform to inspect dataset health in real time, apply targeted or automated cleaning algorithms, compute descriptive statistics, render interactive charts, and export a polished dataset alongside an audit report changelog.

---

## 🌟 2. Key Features

- **Intuitive Desktop GUI:** Clean tabbed notebook layout (`ttk.Notebook`) featuring a spreadsheet viewer (`ttk.Treeview`), statistical cards, embedded chart canvas, and audit logs.
- **Real-Time Health Check Badge:** Visual indicators that track:
  - Total rows and columns
  - Duplicate row count (`⚠️ Warning` when duplicates exist, `✅ Green` when 0)
  - Missing cell count
  - Column name formatting status
- **Targeted & Automated Cleaning Suite:**
  - 🔤 **Standardize Headers:** Strips whitespace, converts to lowercase, and replaces special characters with clean underscores.
  - 🗑️ **Remove Duplicates:** Automatically detects and removes repeat rows.
  - 🩹 **Handle Missing Values:** Modal dialog supporting **Mean**, **Median**, **Mode**, **Custom Value**, or **Row Deletion**.
  - ✂️ **Trim Whitespace:** Removes leading and trailing whitespace across all string columns.
  - ⚡ **Auto-Clean All (One-Click):** Executes an end-to-end cleaning pipeline with a single click.
- **Exploratory Data Analysis (EDA):**
  - **Five-Number Summary:** Count, Mean, Std Dev, Min, 25%, Median (50%), 75%, and Max for all numeric features.
  - **Categorical Breakdown:** Frequencies and percentage distributions for any selected text column.
  - **Correlation Matrix:** Pearson correlation matrix between numerical features.
- **Embedded Matplotlib Visualizations:**
  - Histograms with distribution spreads
  - Categorical bar charts
  - Boxplots for outlier detection
  - Correlation heatmaps
- **Audit Changelog & Clean Export:**
  - Exports clean CSV files ready for machine learning or reporting.
  - Generates a timestamped `.txt` audit report recording every action taken.
  - Instant **"Reset to Original"** button to restart the demonstration at any time.
- **Pre-Bundled Messy Datasets:**
  - `sample_students_dirty.csv`: Academic records with missing marks and repeat students.
  - `sample_sales_dirty.csv`: Commercial transaction records with missing revenues and duplicates.

---

## 📂 3. Project Architecture

```
c:\python project\
├── data/
│   ├── sample_students_dirty.csv   # Pre-bundled dirty academic dataset
│   └── sample_sales_dirty.csv      # Pre-bundled dirty sales dataset
├── core/
│   ├── __init__.py
│   ├── data_manager.py             # DataFrame state, health metrics, and raw backup
│   ├── cleaner.py                  # Pure data transformation functions
│   ├── stats_engine.py             # Descriptive statistics and frequency calculations
│   ├── audit_logger.py             # In-memory changelog and audit report formatter
│   └── exporter.py                 # Safe CSV and text report exporter
├── gui/
│   ├── __init__.py
│   ├── app.py                      # Root Tkinter window, layout, and event wiring
│   ├── table_view.py               # Spreadsheet preview using ttk.Treeview
│   ├── analytics_view.py           # Statistical summary tabs and tables
│   ├── chart_view.py               # Embedded Matplotlib canvas (FigureCanvasTkAgg)
│   └── dialogs.py                  # User input dialogs for column & missing value strategies
├── tests/
│   ├── __init__.py
│   ├── test_data_manager.py        # Unit tests for DataManager & health indicators
│   ├── test_cleaner.py             # Unit tests for data cleaning algorithms
│   └── test_stats_exporter.py      # Unit tests for analytics & export modules
├── main.py                         # Application launcher
├── run_tests.py                    # Automated test runner with formatted terminal output
├── requirements.txt                # External dependencies (pandas, numpy, matplotlib)
└── README.md                       # Documentation, architecture, and viva guide
```

---

## 💻 4. Installation & How to Run

### Step 1: Clone or Open the Project
Open your terminal or command prompt inside the project folder:
```bash
cd "c:\python project"
```

### Step 2: Install Required Libraries
```bash
pip install -r requirements.txt
```
*(Note: `tkinter` is built into Python on Windows and macOS).*

### Step 3: Run the Application
```bash
python main.py
```

### Step 4: Run the Automated Unit Tests
```bash
python run_tests.py
```

---

## 🎯 5. The 2-Minute Practical Exam Demonstration Script

Follow this step-by-step walkthrough in front of your examiner:

1. **Introduction:**
   > *"Good morning/afternoon Sir/Ma'am. My project is a **CSV Data Cleaner & Analytics Studio** built with Tkinter, Pandas, and Matplotlib. It automates dataset health diagnosis, data cleaning, and statistical visualization."*

2. **Load the Messy Data ("The Before State"):**
   - Click the toolbar button **`🎓 Load Students Sample`**.
   - Point to the **Dataset Health Check** panel on the right:
     - Notice the red badges: `⚠️ Duplicates: 4`, `⚠️ Missing Cells: 6`, `⚠️ Headers: Irregular`.
   - Point to the table preview: show the examiner the blank `<NaN>` marks, duplicate student rows, and column names with spaces like `"  Student_ID  "`.

3. **Demonstrate Targeted Cleaning ("The Transformation"):**
   - Click **`🔤 Standardize Column Headers`** ➔ Column names become lowercase and clean (`student_id`, `marks`).
   - Click **`🗑️ Remove Duplicate Rows`** ➔ Duplicate counter drops to `✅ Duplicates: 0`.
   - Click **`🩹 Handle Missing Values...`** ➔ Choose `marks`, select `Fill with Median`, and click Apply ➔ All `<NaN>` marks are instantly filled with calculated medians.
   - Or, simply click **`✨ Auto-Clean All (One-Click)`** to see every health indicator turn **Green ✅**.

4. **Showcase Statistical Analytics:**
   - Switch to the **`📈 Summary Statistics`** tab.
   - Show the calculated Mean, Median, Min, Max, and Standard Deviation for `marks` and `age`.
   - Switch to the **`Categorical Frequencies`** tab and show the distribution of students across departments.

5. **Showcase Visual Charts:**
   - Switch to the **`📊 Visual Charts`** tab.
   - Select `marks`, pick `Histogram / Distribution`, and click **`📊 Render Chart`**.
   - Show the embedded Matplotlib distribution graph directly inside the window!

6. **Export & Reset:**
   - Click **`💾 Save Cleaned CSV`** and **`📄 Export Audit Log`** to show output generation.
   - Click **`🔄 Reset to Original`** if the examiner asks to see the process again from scratch.

---

## 🧠 6. Top 10 Viva Voce Questions & Model Answers

### Q1. Why did you use Pandas instead of standard Python lists and dictionaries?
> **Answer:** Pandas DataFrames are optimized in C for tabular data. They provide vectorized operations, native support for handling missing data (`isna()`, `fillna()`), built-in deduplication (`drop_duplicates()`), and high-performance summary statistics (`describe()`) that would require dozens of lines of nested loops if written using standard lists.

### Q2. How did you embed Matplotlib charts inside a Tkinter window?
> **Answer:** We used `FigureCanvasTkAgg` from `matplotlib.backends.backend_tkagg`. It takes a Matplotlib `Figure` object and turns it into a native Tkinter widget using `.get_tk_widget().pack()`, allowing graphs to render inside our UI without opening a separate pop-up window.

### Q3. When should you fill missing values with Mean versus Median?
> **Answer:** 
> - **Mean** is best when the data is normally distributed (bell-shaped) without extreme outliers.
> - **Median** is preferred when the dataset is skewed or contains extreme outliers (e.g., salaries or house prices), because the median represents the 50th percentile and is resistant to outliers.

### Q4. What is Object-Oriented Programming (OOP) and how is it used here?
> **Answer:** OOP structures code into classes with encapsulated state and methods. In this project:
> - `DataManager` encapsulates dataset loading, health state, and raw backups.
> - `TableView`, `AnalyticsView`, and `ChartView` inherit from `ttk.Frame` to encapsulate modular UI views.
> - `AuditLogger` encapsulates history tracking. This separation of concerns prevents monolithic code and makes the application testable and maintainable.

### Q5. What happens if a user selects a non-numeric column when generating a Histogram?
> **Answer:** The application uses type-checking (`pd.api.types.is_numeric_dtype`). If a text column is selected, it prevents a runtime crash and displays a helpful Tkinter `messagebox.showerror` explaining that a histogram requires numeric data and suggests switching to a Bar Chart.

### Q6. How does your "Reset to Original" feature work?
> **Answer:** When a file is loaded, `DataManager` creates two separate deep copies: `self.raw_df` and `self.current_df` using `df.copy(deep=True)`. All transformations modify `current_df`, while `raw_df` remains completely untouched in memory as an immutable restore snapshot.

### Q7. How does `ttk.Treeview` handle thousands of rows without freezing the GUI?
> **Answer:** We cap the rendered table preview to the first 500 rows while displaying the total row count in an info label. The underlying calculations and exports always process 100% of the dataset in memory, ensuring the UI remains fast and responsive.

### Q8. What is the difference between `ttk` and standard `tk` widgets?
> **Answer:** `ttk` (Themed Tkinter) provides modern, native-looking widgets that adapt to the host operating system's theme, whereas legacy `tk` widgets look outdated and cannot be styled as easily.

### Q9. How do you prevent duplicate columns when standardizing headers?
> **Answer:** If two headers standardize to the same string (e.g., `"Marks"` and `" marks "` both become `"marks"`), our `standardize_headers()` function tracks previously seen names in a dictionary and appends an incremental counter (e.g., `marks_1`), preventing column collisions.

### Q10. How did you verify the reliability of your code?
> **Answer:** We implemented automated unit tests using Python's standard `unittest` framework covering data loading, duplicate removal, header normalization, missing value imputation strategies, summary statistics, and file exports. All 20 test cases pass cleanly via `python run_tests.py`.

---

## 🏆 7. Summary for Examination Evaluators
- **Language:** Python 3.8+
- **GUI Framework:** Tkinter & ttk
- **Data Manipulation:** Pandas & NumPy
- **Data Visualization:** Matplotlib (via TkAgg)
- **Testing Framework:** `unittest` (20 automated tests, 100% passing)
- **Code Quality:** PEP 8 compliant, type-annotated, modular architecture
