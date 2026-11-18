"""Table View module.

Provides a scrollable spreadsheet view using ttk.Treeview with
horizontal and vertical scrollbars.
"""

from typing import Optional
import tkinter as tk
from tkinter import ttk
import pandas as pd


class TableView(ttk.Frame):
    """A responsive table widget using ttk.Treeview to render DataFrame contents."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Scrollbars
        self.v_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.h_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL)

        # Treeview
        self.tree = ttk.Treeview(
            self,
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set,
            selectmode="browse",
            show="headings",
        )

        self.v_scroll.config(command=self.tree.yview)
        self.h_scroll.config(command=self.tree.xview)

        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        # Info label for row count cap
        self.info_label = ttk.Label(
            self,
            text="No data loaded.",
            font=("Segoe UI", 9, "italic"),
            foreground="#555555",
        )
        self.info_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)

    def update_data(self, df: pd.DataFrame, max_rows: int = 500) -> None:
        """Clears and repopulates the table with data from a pandas DataFrame."""
        self.clear()

        if df is None or df.empty:
            self.info_label.config(text="Dataset is empty.")
            return

        columns = [str(c) for c in df.columns]
        self.tree["columns"] = columns

        for col in columns:
            self.tree.heading(col, text=col, anchor="w")
            # Dynamic column width calculation based on header length
            col_width = max(len(col) * 12, 100)
            self.tree.column(col, width=col_width, minwidth=60, anchor="w")

        # Insert rows (capped at max_rows for UI responsiveness)
        display_df = df.iloc[:max_rows]
        for idx, row in display_df.iterrows():
            # Format NaNs as clearly visible "<NaN>" text
            values = [
                "<NaN>" if pd.isna(val) else str(val)
                for val in row
            ]
            self.tree.insert("", "end", values=values)

        total_rows = len(df)
        if total_rows > max_rows:
            self.info_label.config(
                text=f"Showing first {max_rows} of {total_rows} rows (scrollable). Total columns: {len(columns)}"
            )
        else:
            self.info_label.config(
                text=f"Showing all {total_rows} rows. Total columns: {len(columns)}"
            )

    def clear(self) -> None:
        """Clears all rows and column definitions from the tree."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree["columns"] = ()
        self.info_label.config(text="No data loaded.")
