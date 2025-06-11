import os
import sys

sys.path.insert(0, os.path.abspath("src"))

import tkinter as tk

from ui.app import App


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
