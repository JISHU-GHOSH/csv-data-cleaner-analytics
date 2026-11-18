from typing import Optional
import tkinter as tk
from tkinter import ttk
import pandas as pd
from core.stats_engine import (
    get_numeric_summary,
    get_categorical_summary,
    get_correlation_matrix,
)

class AnalyticsView(ttk.Frame):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.current_df: Optional[pd.DataFrame] = None
        self._build_ui()

    def _build_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.num_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.num_frame, text="Numeric Summary (Five-Number)")
        self._build_numeric_tab()

        self.cat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cat_frame, text="Categorical Frequencies")
        self._build_categorical_tab()

        self.corr_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.corr_frame, text="Correlation Matrix")
        self._build_correlation_tab()

    def _build_numeric_tab(self):
        self.num_tree = ttk.Treeview(self.num_frame, selectmode="browse", show="headings")
        v_scroll = ttk.Scrollbar(self.num_frame, orient=tk.VERTICAL, command=self.num_tree.yview)
        h_scroll = ttk.Scrollbar(self.num_frame, orient=tk.HORIZONTAL, command=self.num_tree.xview)
        self.num_tree.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.num_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

    def _build_categorical_tab(self):
        top_bar = ttk.Frame(self.cat_frame)
        top_bar.pack(fill="x", padx=10, pady=8)

        ttk.Label(top_bar, text="Select Categorical Column:", font=("Segoe UI", 9, "bold")).pack(
            side="left", padx=5
        )
        self.cat_col_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(
            top_bar, textvariable=self.cat_col_var, state="readonly", width=25
        )
        self.cat_combo.pack(side="left", padx=5)
        self.cat_combo.bind("<<ComboboxSelected>>", self._on_cat_col_selected)

        self.cat_tree = ttk.Treeview(
            self.cat_frame,
            columns=("Category", "Count", "Percentage (%)"),
            show="headings",
            selectmode="browse",
        )
        for col in ("Category", "Count", "Percentage (%)"):
            self.cat_tree.heading(col, text=col)
            self.cat_tree.column(col, width=150, anchor="center")

        v_scroll = ttk.Scrollbar(self.cat_frame, orient=tk.VERTICAL, command=self.cat_tree.yview)
        self.cat_tree.config(yscrollcommand=v_scroll.set)

        self.cat_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        v_scroll.pack(side="right", fill="y")

    def _build_correlation_tab(self):
        self.corr_tree = ttk.Treeview(self.corr_frame, selectmode="browse", show="headings")
        v_scroll = ttk.Scrollbar(self.corr_frame, orient=tk.VERTICAL, command=self.corr_tree.yview)
        h_scroll = ttk.Scrollbar(self.corr_frame, orient=tk.HORIZONTAL, command=self.corr_tree.xview)
        self.corr_tree.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.corr_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")

    def update_stats(self, df: pd.DataFrame):
        self.current_df = df
        if df is None or df.empty:
            self._clear_all()
            return

        num_summary = get_numeric_summary(df)
        self._populate_tree(self.num_tree, num_summary, include_index=True)

        all_cols = list(df.columns)
        self.cat_combo["values"] = all_cols
        if all_cols:
            self.cat_combo.current(0)
            self._on_cat_col_selected()

        corr_matrix = get_correlation_matrix(df)
        self._populate_tree(self.corr_tree, corr_matrix, include_index=True)

    def _on_cat_col_selected(self, event=None):
        col = self.cat_col_var.get()
        if not col or self.current_df is None or col not in self.current_df.columns:
            return

        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)

        cat_summary = get_categorical_summary(self.current_df, col)
        for val, row in cat_summary.iterrows():
            display_val = "<Missing/NaN>" if pd.isna(val) else str(val)
            self.cat_tree.insert(
                "", "end", values=(display_val, int(row["count"]), f"{row['percentage']}%")
            )

    def _populate_tree(
        self, tree: ttk.Treeview, df: pd.DataFrame, include_index: bool = False
    ):
        for item in tree.get_children():
            tree.delete(item)

        if df.empty:
            tree["columns"] = ("Message",)
            tree.heading("Message", text="No numeric data available")
            tree.column("Message", width=300)
            tree.insert("", "end", values=("No numeric columns found in dataset.",))
            return

        cols = (["Metric / Feature"] + list(df.columns)) if include_index else list(df.columns)
        tree["columns"] = cols

        for col in cols:
            tree.heading(col, text=str(col), anchor="w")
            tree.column(col, width=max(len(str(col)) * 12, 100), anchor="w")

        for idx, row in df.iterrows():
            vals = ([str(idx)] + [str(v) for v in row]) if include_index else [str(v) for v in row]
            tree.insert("", "end", values=vals)

    def _clear_all(self):
        for tree in (self.num_tree, self.cat_tree, self.corr_tree):
            for item in tree.get_children():
                tree.delete(item)
            tree["columns"] = ()
        self.cat_combo["values"] = []
        self.cat_col_var.set("")
