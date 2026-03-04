import tkinter as tk
from gui import launch_gui
import multiprocessing
import sys
import os
import ctypes

# pyinstaller main.py --clean --onefile --noconsole --icon=assets/ABRACADABRA.ico --hidden-import=hampel --name ABRACADABRA --noconfirm --add-data "assets;assets" --collect-data hdmf --collect-data pynwb --collect-submodules hdmf --collect-submodules pynwb --collect-all neuroconv --collect-all ndx_dandi_icephys 

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    root.tk.call("tk", "scaling", 1.25)
    root.title("ABRACADABRA")
    root.geometry

    try:   
        icon_path = resource_path("assets/ABRACADABRA.ico")
        root.iconbitmap(icon_path)
    except Exception:
        print("Icon Not found, continuing without it")

    multiprocessing.freeze_support()

    launch_gui(root)

    root.mainloop()