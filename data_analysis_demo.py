"""
Academic Project: Student Performance Analytics & Preprocessing Pipeline
Subject: Python Programming Practical Examination
Libraries Used: Pandas, NumPy, Matplotlib

Description:
This script demonstrates an end-to-end data pipeline:
1. Data Ingestion & Quality Audit (Pandas)
2. Cleaning, Deduplication & Imputation (Pandas)
3. Vectorized Math, Outlier Detection (IQR) & Grading (NumPy)
4. Group-Level Aggregation & Performance Metrics (Pandas)
5. Statistical Visualizations & Multi-Panel Plotting (Matplotlib)
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load_and_inspect(filepath: str) -> pd.DataFrame:
    """Step 1: Load raw CSV dataset using Pandas and perform initial inspection."""
    print("=" * 70)
    print("STEP 1: DATA INGESTION & QUALITY INSPECTION (PANDAS)")
    print("=" * 70)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at: {filepath}")

    # Load dataset into Pandas DataFrame
    df = pd.read_csv(filepath)
    print(f"Loaded dataset successfully from '{filepath}'")
    print(f"Initial Dimensions: {df.shape[0]} rows x {df.shape[1]} columns\n")

    print("Raw Column Headers:")
    print(list(df.columns))

    print("\nInitial Missing Values per Column:")
    null_counts = df.isnull().sum()
    for col, count in null_counts.items():
        print(f" - {col.strip()}: {count} missing")

    duplicate_rows = df.duplicated().sum()
    print(f"\nInitial Duplicate Records Detected: {duplicate_rows}")
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Step 2: Clean column names, remove duplicates, and impute missing values."""
    print("\n" + "=" * 70)
    print("STEP 2: DATA PREPROCESSING & CLEANING (PANDAS)")
    print("=" * 70)

    clean_df = df.copy()

    # 1. Standardize column names (strip whitespace, lowercase, snake_case)
    clean_df.columns = [col.strip().lower().replace(" ", "_") for col in clean_df.columns]
    print("Standardized Column Headers:")
    print(list(clean_df.columns))

    # 2. Trim string whitespace in text columns
    str_cols = clean_df.select_dtypes(include=["object", "string", str]).columns
    for col in str_cols:
        clean_df[col] = clean_df[col].astype(str).str.strip().replace("nan", np.nan)
    print("Trimmed extraneous whitespace from categorical text fields.")

    # 3. Deduplicate rows
    before_dup = len(clean_df)
    clean_df = clean_df.drop_duplicates()
    dropped_dups = before_dup - len(clean_df)
    print(f"Deduplication complete: dropped {dropped_dups} duplicate records.")

    # 4. Handle missing values:
    # - Numeric columns (age, marks, attendance_pct): fill with median
    # - Categorical columns (department): fill with mode (most frequent)
    num_cols = ["age", "marks", "attendance_pct"]
    for col in num_cols:
        if col in clean_df.columns:
            median_val = clean_df[col].median()
            clean_df[col] = clean_df[col].fillna(median_val)
            print(f"Imputed missing values in '{col}' using median = {median_val:.1f}")

    if "department" in clean_df.columns:
        mode_val = clean_df["department"].mode()[0]
        clean_df["department"] = clean_df["department"].fillna(mode_val)
        print(f"Imputed missing values in 'department' using mode = '{mode_val}'")

    print(f"\nCleaned Dimensions: {clean_df.shape[0]} rows x {clean_df.shape[1]} columns")
    return clean_df

def numpy_vectorized_analytics(df: pd.DataFrame) -> pd.DataFrame:
    """Step 3: Vectorized numerical computations and outlier analysis using NumPy."""
    print("\n" + "=" * 70)
    print("STEP 3: VECTORIZED NUMERICAL ANALYTICS & IQR (NUMPY)")
    print("=" * 70)

    # Convert Pandas Series to NumPy 1D array
    marks_array = df["marks"].to_numpy(dtype=float)
    attendance_array = df["attendance_pct"].to_numpy(dtype=float)

    # 1. Core NumPy statistical functions
    mean_marks = np.mean(marks_array)
    std_marks = np.std(marks_array)
    var_marks = np.var(marks_array)
    min_marks = np.min(marks_array)
    max_marks = np.max(marks_array)

    print("NumPy Array Statistics for Marks:")
    print(f" - Mean:     {mean_marks:.2f}")
    print(f" - Std Dev:  {std_marks:.2f}")
    print(f" - Variance: {var_marks:.2f}")
    print(f" - Range:    [{min_marks:.1f} - {max_marks:.1f}]")

    # 2. Statistical Outlier Detection using Tukey's Interquartile Range (IQR) with NumPy
    q25, q75 = np.percentile(marks_array, [25, 75])
    iqr = q75 - q25
    lower_bound = q25 - (1.5 * iqr)
    upper_bound = q75 + (1.5 * iqr)

    print(f"\nIQR Outlier Thresholds for Marks:")
    print(f" - Q1 (25th Percentile): {q25:.2f}")
    print(f" - Q3 (75th Percentile): {q75:.2f}")
    print(f" - IQR:                 {iqr:.2f}")
    print(f" - Valid Range:         [{lower_bound:.2f}, {upper_bound:.2f}]")

    # NumPy boolean masking to detect anomalies
    outlier_mask = (marks_array < lower_bound) | (marks_array > upper_bound)
    outliers = marks_array[outlier_mask]
    print(f" - Outlier Count:        {len(outliers)} values: {list(outliers)}")

    # 3. Vectorized feature engineering using np.select (Academic Grading)
    conditions = [
        marks_array >= 90.0,
        marks_array >= 80.0,
        marks_array >= 70.0,
        marks_array >= 60.0
    ]
    grades = ["Grade A+", "Grade A", "Grade B", "Grade C"]
    df["performance_grade"] = np.select(conditions, grades, default="Needs Attention")

    # 4. NumPy linear weighting: Composite Index = 70% Marks + 30% Attendance
    df["composite_score"] = np.round((0.70 * marks_array) + (0.30 * attendance_array), 2)
    print("\nCalculated Composite Scores and Letter Grades via vectorized NumPy operations.")

    return df

def aggregate_insights(df: pd.DataFrame):
    """Step 4: Department-wise grouping and summary statistics using Pandas."""
    print("\n" + "=" * 70)
    print("STEP 4: DEPARTMENT-LEVEL AGGREGATIONS (PANDAS GROUPBY)")
    print("=" * 70)

    summary = df.groupby("department").agg(
        student_count=("student_id", "count"),
        avg_marks=("marks", "mean"),
        avg_attendance=("attendance_pct", "mean"),
        top_score=("marks", "max")
    ).reset_index()

    # Round numerical metrics
    summary["avg_marks"] = summary["avg_marks"].round(2)
    summary["avg_attendance"] = summary["avg_attendance"].round(2)

    print(summary.to_string(index=False))
    return summary

def generate_visualizations(df: pd.DataFrame, dept_summary: pd.DataFrame, output_image: str):
    """Step 5: Visualizations using Matplotlib (Multi-panel dashboard figure)."""
    print("\n" + "=" * 70)
    print("STEP 5: STATISTICAL VISUALIZATIONS (MATPLOTLIB)")
    print("=" * 70)

    # Set up a professional 3-panel figure
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Student Performance Analytics - Statistical Overview", fontsize=15, fontweight="bold", y=1.03)

    # 1. Histogram: Marks Distribution with Mean Line
    ax1 = axes[0]
    marks = df["marks"].to_numpy()
    mean_val = np.mean(marks)
    ax1.hist(marks, bins=7, color="#E5322D", edgecolor="#111111", alpha=0.85)
    ax1.axvline(mean_val, color="#161616", linestyle="dashed", linewidth=2, label=f"Mean: {mean_val:.1f}")
    ax1.set_title("Distribution of Student Marks", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Marks", fontsize=10)
    ax1.set_ylabel("Student Count", fontsize=10)
    ax1.legend()
    ax1.grid(True, linestyle=":", alpha=0.5)

    # 2. Boxplot: Marks Spread & Quartiles
    ax2 = axes[1]
    box = ax2.boxplot(marks, patch_artist=True, boxprops=dict(facecolor="#FEE2E2", color="#E5322D", linewidth=1.5),
                      medianprops=dict(color="#B91C1C", linewidth=2),
                      whiskerprops=dict(color="#161616", linewidth=1.2),
                      capprops=dict(color="#161616", linewidth=1.2))
    ax2.set_title("Boxplot (Five-Number Summary)", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Marks Scale", fontsize=10)
    ax2.set_xticklabels(["Overall Cohort"])
    ax2.grid(True, linestyle=":", alpha=0.5)

    # 3. Bar Chart: Department Average Marks
    ax3 = axes[2]
    depts = dept_summary["department"]
    avg_marks = dept_summary["avg_marks"]
    colors = ["#2563EB", "#059669", "#D97706", "#7C3AED"][:len(depts)]
    bars = ax3.bar(depts, avg_marks, color=colors, edgecolor="#333333", width=0.55)
    ax3.set_title("Average Marks by Department", fontsize=12, fontweight="bold")
    ax3.set_xlabel("Department", fontsize=10)
    ax3.set_ylabel("Average Marks", fontsize=10)
    ax3.set_ylim(0, 100)
    ax3.tick_params(axis='x', rotation=15)
    ax3.grid(axis='y', linestyle=":", alpha=0.5)

    # Add data labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax3.annotate(f"{height:.1f}",
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_image, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Chart figure successfully saved to: '{output_image}'")

def main():
    """Main execution pipeline."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, "data", "sample_students_dirty.csv")
    output_chart = os.path.join(base_dir, "student_analytics_plots.png")

    print("\n>>> STARTING PYTHON DATA ANALYTICS PIPELINE <<<")
    # Step 1: Load and inspect
    raw_df = load_and_inspect(input_file)

    # Step 2: Clean data
    clean_df = clean_data(raw_df)

    # Step 3: Vectorized NumPy Analytics
    analyzed_df = numpy_vectorized_analytics(clean_df)

    # Step 4: GroupBy Aggregation
    dept_summary = aggregate_insights(analyzed_df)

    # Step 5: Visualizations
    generate_visualizations(analyzed_df, dept_summary, output_chart)

    print("\n" + "=" * 70)
    print("SAMPLE PROCESSED DATA (HEAD 5):")
    print("=" * 70)
    display_cols = ["student_id", "full_name", "department", "marks", "attendance_pct", "performance_grade", "composite_score"]
    print(analyzed_df[display_cols].head(5).to_string(index=False))

    print("\n>>> PIPELINE EXECUTED SUCCESSFULLY (0 ERRORS) <<<\n")

if __name__ == "__main__":
    main()
