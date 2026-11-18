import sys
import tkinter as tk
from gui.app import MainWindow

def main():
    root = tk.Tk()
    try:
        if sys.platform == "win32":
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
