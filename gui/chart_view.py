"""Chart View module.

Embeds interactive Matplotlib visual charts directly inside a Tkinter tab
using FigureCanvasTkAgg.
"""

from typing import Optional
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class ChartView(ttk.Frame):
    """Tab widget for rendering and saving embedded Matplotlib visualizations."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self.current_df: Optional[pd.DataFrame] = None

        self._build_ui()

    def _build_ui(self) -> None:
        # Top Control Toolbar
        control_frame = ttk.LabelFrame(self, text=" Visualization Controls ", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        # 1. Column Selection
        ttk.Label(control_frame, text="Select Column:", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.col_var = tk.StringVar()
        self.col_combo = ttk.Combobox(
            control_frame, textvariable=self.col_var, state="readonly", width=22
        )
        self.col_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # 2. Plot Type Selection
        ttk.Label(control_frame, text="Chart Type:", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=2, padx=15, pady=5, sticky="w"
        )
        self.plot_type_var = tk.StringVar(value="Histogram / Distribution")
        plot_types = [
            "Histogram / Distribution",
            "Bar Chart (Value Counts)",
            "Boxplot (Outlier Detection)",
            "Correlation Heatmap",
        ]
        self.plot_combo = ttk.Combobox(
            control_frame,
            textvariable=self.plot_type_var,
            values=plot_types,
            state="readonly",
            width=26,
        )
        self.plot_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # 3. Action Buttons
        ttk.Button(
            control_frame, text="📊 Render Chart", command=self.render_selected_plot
        ).grid(row=0, column=4, padx=10, pady=5)

        ttk.Button(
            control_frame, text="🧹 Clear Canvas", command=self.clear_canvas
        ).grid(row=0, column=5, padx=5, pady=5)

        # Matplotlib Canvas Area
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.fig = Figure(figsize=(7, 4.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.canvas_frame)
        self.toolbar.update()

        self._draw_placeholder()

    def update_columns(self, df: pd.DataFrame) -> None:
        """Updates available columns dropdown when dataset changes."""
        self.current_df = df
        if df is None or df.empty:
            self.col_combo["values"] = []
            self.col_var.set("")
            self._draw_placeholder()
            return

        columns = list(df.columns)
        self.col_combo["values"] = columns
        if columns:
            # Default to first numeric column if available
            num_cols = df.select_dtypes(include=["number"]).columns
            if len(num_cols) > 0:
                self.col_combo.set(num_cols[0])
            else:
                self.col_combo.set(columns[0])

    def render_selected_plot(self) -> None:
        """Plots the selected column and chart type."""
        if self.current_df is None or self.current_df.empty:
            messagebox.showwarning("No Data", "Please load a dataset first.", parent=self)
            return

        plot_type = self.plot_type_var.get()
        col = self.col_var.get()
        df = self.current_df

        self.ax.clear()

        try:
            if plot_type == "Correlation Heatmap":
                numeric_df = df.select_dtypes(include=["number"])
                if numeric_df.shape[1] < 2:
                    messagebox.showinfo(
                        "Insufficient Numeric Columns",
                        "Correlation heatmap requires at least 2 numeric columns.",
                        parent=self,
                    )
                    self._draw_placeholder()
                    return

                corr = numeric_df.corr()
                cax = self.ax.matshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
                self.fig.colorbar(cax, ax=self.ax)
                self.ax.set_xticks(range(len(corr.columns)))
                self.ax.set_yticks(range(len(corr.columns)))
                self.ax.set_xticklabels(corr.columns, rotation=45, ha="left", fontsize=8)
                self.ax.set_yticklabels(corr.columns, fontsize=8)
                self.ax.set_title("Correlation Heatmap", pad=20, fontsize=12, fontweight="bold")

            elif plot_type == "Histogram / Distribution":
                if not pd.api.types.is_numeric_dtype(df[col]):
                    messagebox.showerror(
                        "Type Error",
                        f"Column '{col}' is not numeric. Cannot plot histogram.\n"
                        "Please choose a numeric column or switch to 'Bar Chart'.",
                        parent=self,
                    )
                    return

                series = df[col].dropna()
                self.ax.hist(series, bins=12, color="#3498db", edgecolor="#2980b9", alpha=0.8)
                self.ax.set_title(f"Distribution of {col}", fontsize=12, fontweight="bold")
                self.ax.set_xlabel(col)
                self.ax.set_ylabel("Frequency")
                self.ax.grid(True, linestyle="--", alpha=0.5)

            elif plot_type == "Bar Chart (Value Counts)":
                counts = df[col].astype(str).value_counts().head(15)
                self.ax.bar(counts.index, counts.values, color="#2ecc71", edgecolor="#27ae60")
                self.ax.set_title(f"Top Categories in {col}", fontsize=12, fontweight="bold")
                self.ax.set_xlabel(col)
                self.ax.set_ylabel("Count")
                self.ax.tick_params(axis="x", rotation=40)
                self.ax.grid(axis="y", linestyle="--", alpha=0.5)

            elif plot_type == "Boxplot (Outlier Detection)":
                if not pd.api.types.is_numeric_dtype(df[col]):
                    messagebox.showerror(
                        "Type Error",
                        f"Column '{col}' is not numeric. Cannot plot boxplot.",
                        parent=self,
                    )
                    return

                series = df[col].dropna()
                self.ax.boxplot(series, vert=True, patch_artist=True,
                                boxprops=dict(facecolor="#f39c12", color="#d35400"))
                self.ax.set_title(f"Boxplot of {col}", fontsize=12, fontweight="bold")
                self.ax.set_ylabel(col)
                self.ax.grid(True, linestyle="--", alpha=0.5)

            self.fig.tight_layout()
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Plotting Error", f"An error occurred while generating plot:\n{str(e)}", parent=self)
            self._draw_placeholder()

    def clear_canvas(self) -> None:
        """Clears chart canvas back to placeholder."""
        self._draw_placeholder()

    def _draw_placeholder(self) -> None:
        self.ax.clear()
        self.ax.text(
            0.5,
            0.5,
            "Select a column & chart type above, then click 'Render Chart'.",
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=11,
            color="#888888",
            transform=self.ax.transAxes,
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()
