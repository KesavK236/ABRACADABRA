import tkinter as tk
from gui import launch_gui
import sys
import os

# pyinstaller --clean --onefile --noconsole --icon=assets/ABRACADABRA.ico --hidden-import=hampel  main.py

# Gets the relative paths for the output files
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ABRACADABRA")
    root.geometry

    try:   
        icon_path = resource_path("assets/ABRACADABRA.ico")
        root.iconbitmap(icon_path)
    except Exception:
        print("Icon Not found, continuing without it")

    launch_gui(root)

    root.mainloop()