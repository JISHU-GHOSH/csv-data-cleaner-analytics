"""CSV Data Cleaner & Analytics Studio.

Main entry point for launching the Tkinter Desktop Application.
"""

import sys
import tkinter as tk
from gui.app import MainWindow


def main() -> None:
    """Initializes and runs the Tkinter application main loop."""
    root = tk.Tk()

    # Configure application icon and appearance if supported
    try:
        # High-DPI awareness on Windows
        if sys.platform == "win32":
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
