"""Main Application Window module.

Integrates the toolbar, sidebar action controls, data view tabs,
and health status indicators into a cohesive Tkinter desktop interface.
"""

import os
from typing import Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

import pandas as pd

from core.data_manager import DataManager
from core.audit_logger import AuditLogger
from core.exporter import save_csv, save_report
import core.cleaner as cleaner

from gui.table_view import TableView
from gui.analytics_view import AnalyticsView
from gui.chart_view import ChartView
from gui.dialogs import show_missing_value_dialog


class MainWindow:
    """The root application window for CSV Data Cleaner & Analytics Studio."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("CSV Data Cleaner & Analytics Studio — End Sem Practical Project")
        self.root.geometry("1180x740")
        self.root.minsize(980, 620)

        # Core State Controllers
        self.data_manager = DataManager()
        self.audit_logger = AuditLogger()

        self._configure_styles()
        self._build_layout()
        self._set_status("Ready. Please load a CSV file or choose a pre-bundled sample.")

    def _configure_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("HealthVal.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Action.TButton", font=("Segoe UI", 9, "bold"), padding=5)

    def _build_layout(self) -> None:
        # 1. Top Toolbar
        self._build_top_toolbar()

        # 2. Main Content Area (Two Columns)
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill="both", expand=True, padx=8, pady=4)

        # Left Notebook (Data Views)
        self.notebook_frame = ttk.Frame(main_paned)
        main_paned.add(self.notebook_frame, weight=3)
        self._build_notebook(self.notebook_frame)

        # Right Sidebar (Control & Cleaning Panel)
        self.sidebar_frame = ttk.Frame(main_paned, width=320)
        main_paned.add(self.sidebar_frame, weight=1)
        self._build_sidebar(self.sidebar_frame)

        # 3. Bottom Status Bar
        self.status_var = tk.StringVar(value="Ready.")
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor="w",
            font=("Segoe UI", 9),
            padding=(8, 4),
        )
        self.status_bar.pack(side="bottom", fill="x")

    def _build_top_toolbar(self) -> None:
        toolbar = ttk.Frame(self.root, padding=(8, 6), relief=tk.RAISED)
        toolbar.pack(side="top", fill="x")

        ttk.Button(toolbar, text="📂 Open CSV...", command=self.on_open_file).pack(
            side="left", padx=3
        )
        ttk.Button(
            toolbar, text="🎓 Load Students Sample", command=lambda: self.on_load_sample("students")
        ).pack(side="left", padx=3)
        ttk.Button(
            toolbar, text="💼 Load Sales Sample", command=lambda: self.on_load_sample("sales")
        ).pack(side="left", padx=3)

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8)

        ttk.Button(toolbar, text="🔄 Reset to Original", command=self.on_reset).pack(
            side="left", padx=3
        )
        ttk.Button(toolbar, text="💾 Save Cleaned CSV", command=self.on_save_csv).pack(
            side="left", padx=3
        )
        ttk.Button(toolbar, text="📄 Export Audit Log", command=self.on_export_report).pack(
            side="left", padx=3
        )

    def _build_notebook(self, parent: ttk.Frame) -> None:
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Spreadsheet Table View
        self.table_view = TableView(self.notebook)
        self.notebook.add(self.table_view, text="  🗂️ Data Table Preview  ")

        # Tab 2: Analytics & Summary
        self.analytics_view = AnalyticsView(self.notebook)
        self.notebook.add(self.analytics_view, text="  📈 Summary Statistics  ")

        # Tab 3: Interactive Visual Charts
        self.chart_view = ChartView(self.notebook)
        self.notebook.add(self.chart_view, text="  📊 Visual Charts  ")

        # Tab 4: Audit Log Viewer
        audit_tab = ttk.Frame(self.notebook)
        self.notebook.add(audit_tab, text="  📝 Audit Log  ")
        self.audit_text = ScrolledText(
            audit_tab, wrap="word", font=("Consolas", 10), state="disabled"
        )
        self.audit_text.pack(fill="both", expand=True, padx=6, pady=6)

    def _build_sidebar(self, parent: ttk.Frame) -> None:
        # Container with padding
        container = ttk.Frame(parent, padding=8)
        container.pack(fill="both", expand=True)

        # 1. Dataset Health Summary Box
        health_frame = ttk.LabelFrame(container, text=" 🔍 Dataset Health Check ", padding=10)
        health_frame.pack(fill="x", pady=(0, 10))

        self.lbl_file = ttk.Label(health_frame, text="File: (None)", font=("Segoe UI", 9, "bold"))
        self.lbl_file.pack(anchor="w", pady=2)

        self.lbl_shape = ttk.Label(health_frame, text="Shape: 0 rows × 0 cols")
        self.lbl_shape.pack(anchor="w", pady=2)

        self.lbl_dups = ttk.Label(health_frame, text="Duplicates: 0", font=("Segoe UI", 9))
        self.lbl_dups.pack(anchor="w", pady=2)

        self.lbl_nulls = ttk.Label(health_frame, text="Missing Cells: 0", font=("Segoe UI", 9))
        self.lbl_nulls.pack(anchor="w", pady=2)

        self.lbl_headers = ttk.Label(health_frame, text="Headers: Clean", font=("Segoe UI", 9))
        self.lbl_headers.pack(anchor="w", pady=2)

        # 2. Automated One-Click Cleaning
        auto_frame = ttk.LabelFrame(container, text=" ⚡ Automated Suite ", padding=8)
        auto_frame.pack(fill="x", pady=5)
        ttk.Button(
            auto_frame,
            text="✨ Auto-Clean All (One-Click)",
            style="Action.TButton",
            command=self.on_auto_clean,
        ).pack(fill="x", pady=2)

        # 3. Individual Step-by-Step Cleaners
        clean_frame = ttk.LabelFrame(container, text=" 🧹 Targeted Cleaners ", padding=8)
        clean_frame.pack(fill="x", pady=5)

        ttk.Button(
            clean_frame,
            text="🔤 Standardize Column Headers",
            command=self.on_standardize_headers,
        ).pack(fill="x", pady=3)

        ttk.Button(
            clean_frame,
            text="🗑️ Remove Duplicate Rows",
            command=self.on_remove_duplicates,
        ).pack(fill="x", pady=3)

        ttk.Button(
            clean_frame,
            text="🩹 Handle Missing (NaN) Values...",
            command=self.on_handle_missing,
        ).pack(fill="x", pady=3)

        ttk.Button(
            clean_frame,
            text="✂️ Trim Whitespace in Text",
            command=self.on_trim_whitespace,
        ).pack(fill="x", pady=3)

        # Quick Viva Hint Box
        viva_frame = ttk.LabelFrame(container, text=" 💡 Viva Tip ", padding=8)
        viva_frame.pack(fill="x", pady=(10, 0))
        ttk.Label(
            viva_frame,
            text="1. Load sample dataset\n2. Show messy stats\n3. Click cleaning tools\n4. Show green health & chart",
            font=("Segoe UI", 8),
            foreground="#444444",
        ).pack(anchor="w")

    # -------------------------------------------------------------
    # Event Handlers & Business Logic
    # -------------------------------------------------------------

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def on_open_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Open CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if not path:
            return

        success, msg = self.data_manager.load_csv(path)
        if success:
            self.audit_logger.clear()
            self.audit_logger.log("File Loaded", f"Loaded '{os.path.basename(path)}'")
            self._refresh_all_views()
            self._set_status(msg)
        else:
            messagebox.showerror("Error", msg, parent=self.root)

    def on_load_sample(self, key: str) -> None:
        success, msg = self.data_manager.load_sample(key)
        if success:
            self.audit_logger.clear()
            sample_name = "Students Dataset (Dirty)" if key == "students" else "Sales Dataset (Dirty)"
            self.audit_logger.log("Sample Loaded", f"Loaded bundled sample: {sample_name}")
            self._refresh_all_views()
            self._set_status(msg)
            messagebox.showinfo(
                "Sample Loaded",
                f"Successfully loaded {sample_name}!\nNotice the duplicates, missing values, and messy headers.",
                parent=self.root,
            )
        else:
            messagebox.showerror("Error", msg, parent=self.root)

    def on_reset(self) -> None:
        if not self.data_manager.has_data():
            messagebox.showwarning("Warning", "No dataset loaded.", parent=self.root)
            return

        success, msg = self.data_manager.reset_to_raw()
        if success:
            self.audit_logger.log("Reset", "Dataset restored to original loaded state.")
            self._refresh_all_views()
            self._set_status(msg)
            messagebox.showinfo("Reset", msg, parent=self.root)

    def on_standardize_headers(self) -> None:
        if not self._check_data_loaded():
            return

        df, msg = cleaner.standardize_headers(self.data_manager.current_df)
        self.data_manager.current_df = df
        self.audit_logger.log("Standardize Headers", msg)
        self._refresh_all_views()
        self._set_status(msg)

    def on_remove_duplicates(self) -> None:
        if not self._check_data_loaded():
            return

        df, msg, count = cleaner.remove_duplicates(self.data_manager.current_df)
        self.data_manager.current_df = df
        self.audit_logger.log("Remove Duplicates", msg)
        self._refresh_all_views()
        self._set_status(msg)
        messagebox.showinfo("Duplicates Cleaned", msg, parent=self.root)

    def on_trim_whitespace(self) -> None:
        if not self._check_data_loaded():
            return

        df, msg = cleaner.trim_whitespace(self.data_manager.current_df)
        self.data_manager.current_df = df
        self.audit_logger.log("Trim Whitespace", msg)
        self._refresh_all_views()
        self._set_status(msg)

    def on_handle_missing(self) -> None:
        if not self._check_data_loaded():
            return

        cols = list(self.data_manager.current_df.columns)
        choice = show_missing_value_dialog(self.root, cols)
        if choice is None:
            return

        col, strategy, custom_val = choice
        df, msg = cleaner.handle_missing(
            self.data_manager.current_df, column=col, strategy=strategy, custom_val=custom_val
        )
        self.data_manager.current_df = df
        self.audit_logger.log("Handle Missing Values", msg)
        self._refresh_all_views()
        self._set_status(msg)
        messagebox.showinfo("Missing Values Handled", msg, parent=self.root)

    def on_auto_clean(self) -> None:
        if not self._check_data_loaded():
            return

        clean_df, logs = cleaner.auto_clean_all(self.data_manager.current_df)
        self.data_manager.current_df = clean_df
        for l in logs:
            self.audit_logger.log("Auto-Clean", l)

        self._refresh_all_views()
        msg = f"Auto-clean completed: applied {len(logs)} automated cleaning steps."
        self._set_status(msg)
        messagebox.showinfo("Auto-Clean Complete", msg + "\n\nAll health metrics are now green!", parent=self.root)

    def on_save_csv(self) -> None:
        if not self._check_data_loaded():
            return

        path = filedialog.asksaveasfilename(
            title="Save Cleaned CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile="cleaned_" + self.data_manager.source_name,
        )
        if not path:
            return

        success, msg = save_csv(self.data_manager.current_df, path)
        if success:
            self.audit_logger.log("Export CSV", f"Saved cleaned dataset to {os.path.basename(path)}")
            self._update_audit_view()
            self._set_status(msg)
            messagebox.showinfo("Saved", msg, parent=self.root)
        else:
            messagebox.showerror("Save Error", msg, parent=self.root)

    def on_export_report(self) -> None:
        if not self.data_manager.has_data():
            messagebox.showwarning("Warning", "No dataset loaded.", parent=self.root)
            return

        path = filedialog.asksaveasfilename(
            title="Export Audit Report",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile="audit_report.txt",
        )
        if not path:
            return

        report_content = self.audit_logger.get_report_text()
        success, msg = save_report(report_content, path)
        if success:
            self._set_status(msg)
            messagebox.showinfo("Report Exported", msg, parent=self.root)
        else:
            messagebox.showerror("Export Error", msg, parent=self.root)

    def _check_data_loaded(self) -> bool:
        if not self.data_manager.has_data():
            messagebox.showwarning("No Data", "Please load a dataset first.", parent=self.root)
            return False
        return True

    def _refresh_all_views(self) -> None:
        df = self.data_manager.current_df
        metrics = self.data_manager.get_health_metrics()

        # Update Health Badge Text and Colors
        self.lbl_file.config(text=f"File: {self.data_manager.source_name}")
        self.lbl_shape.config(text=f"Shape: {metrics['total_rows']} rows × {metrics['total_cols']} cols")

        if metrics["duplicate_count"] > 0:
            self.lbl_dups.config(
                text=f"⚠️ Duplicates: {metrics['duplicate_count']}", foreground="#c0392b"
            )
        else:
            self.lbl_dups.config(text="✅ Duplicates: 0", foreground="#27ae60")

        if metrics["total_missing_cells"] > 0:
            self.lbl_nulls.config(
                text=f"⚠️ Missing Cells: {metrics['total_missing_cells']}", foreground="#c0392b"
            )
        else:
            self.lbl_nulls.config(text="✅ Missing Cells: 0", foreground="#27ae60")

        if metrics["has_unclean_headers"]:
            self.lbl_headers.config(text="⚠️ Headers: Irregular", foreground="#e67e22")
        else:
            self.lbl_headers.config(text="✅ Headers: Clean", foreground="#27ae60")

        # Update Notebook Views
        self.table_view.update_data(df)
        self.analytics_view.update_stats(df)
        self.chart_view.update_columns(df)
        self._update_audit_view()

    def _update_audit_view(self) -> None:
        self.audit_text.config(state="normal")
        self.audit_text.delete("1.0", tk.END)
        self.audit_text.insert(tk.END, self.audit_logger.get_report_text())
        self.audit_text.config(state="disabled")
