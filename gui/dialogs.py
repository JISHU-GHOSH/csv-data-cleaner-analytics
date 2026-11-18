"""Dialogs module.

Provides modal dialog windows for interactive user choices like
handling missing values or selecting columns for analytics/plotting.
"""

from typing import List, Optional, Tuple, Any
import tkinter as tk
from tkinter import ttk, messagebox


class MissingValueDialog(tk.Toplevel):
    """Modal dialog for choosing missing value handling options."""

    def __init__(self, parent: tk.Widget, columns: List[str]) -> None:
        super().__init__(parent)
        self.title("Handle Missing Values")
        self.geometry("420x320")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result: Optional[Tuple[str, str, Optional[Any]]] = None

        self._build_ui(columns)
        self.wait_window(self)

    def _build_ui(self, columns: List[str]) -> None:
        pad_opts = {"padx": 15, "pady": 8}

        # Header Label
        ttk.Label(
            self,
            text="Configure Missing (NaN) Value Handling",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", **pad_opts)

        # 1. Target Column Selection
        col_frame = ttk.Frame(self)
        col_frame.pack(fill="x", **pad_opts)
        ttk.Label(col_frame, text="Target Column:", width=15).pack(side="left")
        self.col_var = tk.StringVar()
        col_choices = ["all"] + list(columns)
        self.col_combo = ttk.Combobox(
            col_frame, textvariable=self.col_var, values=col_choices, state="readonly"
        )
        self.col_combo.current(0)
        self.col_combo.pack(side="left", fill="x", expand=True)

        # 2. Strategy Selection
        strat_frame = ttk.Frame(self)
        strat_frame.pack(fill="x", **pad_opts)
        ttk.Label(strat_frame, text="Cleaning Strategy:", width=15).pack(side="left")
        self.strat_var = tk.StringVar(value="median")
        strategies = [
            ("Fill with Median (Numeric)", "median"),
            ("Fill with Mean (Numeric)", "mean"),
            ("Fill with Mode (Most Frequent)", "mode"),
            ("Fill with Custom Value", "custom"),
            ("Drop Rows with Nulls", "drop_rows"),
        ]
        self.strat_combo = ttk.Combobox(
            strat_frame,
            textvariable=self.strat_var,
            values=[s[1] for s in strategies],
            state="readonly",
        )
        self.strat_combo.current(0)
        self.strat_combo.pack(side="left", fill="x", expand=True)
        self.strat_combo.bind("<<ComboboxSelected>>", self._on_strategy_change)

        # 3. Custom Value Field (initially disabled)
        custom_frame = ttk.Frame(self)
        custom_frame.pack(fill="x", **pad_opts)
        ttk.Label(custom_frame, text="Custom Value:", width=15).pack(side="left")
        self.custom_var = tk.StringVar(value="0")
        self.custom_entry = ttk.Entry(
            custom_frame, textvariable=self.custom_var, state="disabled"
        )
        self.custom_entry.pack(side="left", fill="x", expand=True)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=20, padx=15)
        ttk.Button(btn_frame, text="Apply Fix", command=self._on_apply).pack(
            side="right", padx=5
        )
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(
            side="right", padx=5
        )

    def _on_strategy_change(self, event=None) -> None:
        if self.strat_var.get() == "custom":
            self.custom_entry.config(state="normal")
        else:
            self.custom_entry.config(state="disabled")

    def _on_apply(self) -> None:
        target_col = self.col_var.get()
        strategy = self.strat_var.get()
        custom_val = self.custom_var.get() if strategy == "custom" else None

        if strategy == "custom" and not custom_val.strip():
            messagebox.showwarning("Input Error", "Please specify a custom value.", parent=self)
            return

        self.result = (target_col, strategy, custom_val)
        self.destroy()


class ColumnPickerDialog(tk.Toplevel):
    """Simple modal dialog to choose a column from a list."""

    def __init__(
        self, parent: tk.Widget, columns: List[str], title: str = "Select Column", prompt: str = "Choose a column:"
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.geometry("360x180")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.selected_column: Optional[str] = None
        self._build_ui(columns, prompt)
        self.wait_window(self)

    def _build_ui(self, columns: List[str], prompt: str) -> None:
        ttk.Label(self, text=prompt, font=("Segoe UI", 10)).pack(
            anchor="w", padx=20, pady=(20, 10)
        )

        self.col_var = tk.StringVar()
        self.combo = ttk.Combobox(
            self, textvariable=self.col_var, values=columns, state="readonly"
        )
        if columns:
            self.combo.current(0)
        self.combo.pack(fill="x", padx=20, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=20)
        ttk.Button(btn_frame, text="Select", command=self._on_select).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)

    def _on_select(self) -> None:
        self.selected_column = self.col_var.get()
        self.destroy()


def show_missing_value_dialog(
    parent: tk.Widget, columns: List[str]
) -> Optional[Tuple[str, str, Optional[Any]]]:
    """Helper function to show the MissingValueDialog and return result."""
    dialog = MissingValueDialog(parent, columns)
    return dialog.result


def show_column_picker_dialog(
    parent: tk.Widget, columns: List[str], title: str = "Select Column", prompt: str = "Choose a column:"
) -> Optional[str]:
    """Helper function to show the ColumnPickerDialog and return selected column."""
    dialog = ColumnPickerDialog(parent, columns, title=title, prompt=prompt)
    return dialog.selected_column
