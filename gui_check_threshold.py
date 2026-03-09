import tkinter as tk
from PIL import ImageTk, Image
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import sys
import os
import numpy as np
from logic.processing import generate_derivatives


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



def thresh_good_button(check_threshold_window):
    """Handle the event when the user confirms that the calculated threshold is good, setting the decision variable accordingly and closing the window."""
    global decision
    decision = 1
    check_threshold_window.destroy()


def window_button(check_threshold_window):
    """Handle the event when the user opts to search for the threshold within a specified window, setting the decision variable accordingly and closing the window."""
    global decision
    decision = 0
    check_threshold_window.destroy()



def sweep_increase(check_threshold_window):
    """Handle the event when the user opts to check the next sweep, setting the decision variable accordingly and closing the window."""
    global decision
    decision = 2
    check_threshold_window.destroy()



def check_thresh_window(check_thresh, upper_window, lower_window, sweep_x, sweep_y, threshold_index, curr_start_index, current_end_index):
    """Display a GUI window for the user to verify the calculated threshold and optionally specify a search window for recalculating the threshold.
    Parameters
    ----------
    check_thresh : bool
        Whether to show the threshold verification UI or not.
    upper_window : float
        Initial upper bound of the search window in seconds.
    lower_window : float
        Initial lower bound of the search window in seconds.
    sweep_x : numpy.ndarray
        Time values of the current sweep.
    sweep_y : numpy.ndarray
        Voltage values of the current sweep.
    threshold_index : int
        Index of the calculated threshold within the sweep data.
    curr_start_index : int
        Index of the start of the current injection within the sweep data.
    current_end_index : int
        Index of the end of the current injection within the sweep data.
    
    Returns
    -------
    tuple
        A tuple containing the user's decision (1 for threshold is good, 0 for search in window, 2 for check next sweep) and the potentially updated upper and lower bounds of the search window.
    """
    global decision
    global window_width


    if check_thresh == False:
        decision = 1
        return decision, upper_window, lower_window


    check_threshold_window = tk.Toplevel()
    check_threshold_window.title("Check Threshold")
    check_threshold_window.geometry("1284x800")
    window_width = 1284

    try:   
        icon_path = resource_path("assets/ABRACADABRA.ico")
        check_thresh_window.iconbitmap(icon_path)
    except Exception:
        print("Icon Not found, continuing without it")

    title_label = tk.Label(check_threshold_window, text="Verify the Calculated Threshold", font=('Verdana', 16))
    title_label.grid(column=0, columnspan=6, row=0)

    frame_left = tk.Frame(check_threshold_window, highlightbackground="black", highlightthickness=1)
    frame_left.grid(row=1, column=0, columnspan=3, sticky="nsew")

    frame_right = tk.Frame(check_threshold_window, highlightbackground="black", highlightthickness=1)
    frame_right.grid(row=1, column=3, columnspan=3, sticky="nsew")


    fig1, ax1 = plt.subplots()
    ax1.plot(sweep_x, sweep_y)
    ax1.plot(sweep_x[threshold_index], sweep_y[threshold_index], 'go')
    ax1.set_title("Standard Trace")

    canvas1 = FigureCanvasTkAgg(fig1, master=frame_left)
    toolbar1 = NavigationToolbar2Tk(canvas1, frame_left)
    toolbar1.update()

    toolbar1.grid(row=0, column=0, sticky="ew")
    canvas1.get_tk_widget().grid(row=1, column=0, sticky="nsew")

    fig2, ax2 = plt.subplots()
    yd, xd, yd2, xd2 = generate_derivatives(sweep_x, sweep_y)
    ax2.plot(xd, yd)
    ax2.plot(xd[threshold_index], yd[threshold_index], 'go')
    ax2.set_title("Derivative Trace") 
    canvas2 = FigureCanvasTkAgg(fig2, master=frame_right)
    toolbar2 = NavigationToolbar2Tk(canvas2, frame_right)
    toolbar2.update()
    
    toolbar2.grid(row=0, column=0, sticky="ew")
    canvas2.get_tk_widget().grid(row=1, column=0, sticky="nsew")


    # windowed search
    window_upper_limit_label = tk.Label(check_threshold_window, text="Upper Bound(sec):", font=('Verdana', 12))
    window_upper_limit_label.grid(column=0, row=2, sticky='e', pady= 5)

    upper_entry = tk.StringVar()
    upper_entry.set(str(upper_window))
    window_upper_limit_entry = tk.Entry(check_threshold_window, width=8, textvariable=upper_entry, font=('Verdana', 12))
    window_upper_limit_entry.grid(column=1, row=2, sticky= 'w')

    window_lower_limit_label = tk.Label(check_threshold_window, text="Lower Bound (sec):", font=('Verdana', 12))
    window_lower_limit_label.grid(column=0, row=3, sticky='e')

    lower_entry = tk.StringVar()
    lower_entry.set(str(lower_window))
    window_lower_limit_entry = tk.Entry(check_threshold_window, width=8, textvariable=lower_entry, font=('Verdana', 12))
    window_lower_limit_entry.grid(column=1, row=3, sticky='w')

    decision = 0
    # Decision buttons
    button_thresh_window = tk.Button(check_threshold_window, text="Search in this window", width=20, height=1, bg="grey", fg="black",
                                    command=lambda: window_button(check_threshold_window), font=('Verdana', 12))
    button_thresh_window.grid(column=0, columnspan=2, row=4, sticky='s')
    button_thresh_good = tk.Button(check_threshold_window, text="Threshold is good!", width=20, height=1, bg="grey", fg="black",
                                    command=lambda: thresh_good_button(check_threshold_window), font=('Verdana', 12))
    button_thresh_good.grid(column=2, columnspan=2, row=4, sticky='s')
    button_sweep_increase = tk.Button(check_threshold_window, text="Check next sweep", width=20, height=1, bg="grey", fg="black",
                                    command=lambda: sweep_increase(check_threshold_window), font=('Verdana', 12))
    button_sweep_increase.grid(column=4, columnspan=2, row=4, sticky='s')



    def on_closing():
        """
        Handles the window closing event.
        """
        global decision
        decision = 0
        mgr = fig1.canvas.manager
        if mgr is not None:
            mgr.destroy()
        mgr2 = fig2.canvas.manager
        if mgr2 is not None:
            mgr2.destroy()
        toolbar1.destroy()
        toolbar2.destroy()
        canvas1.get_tk_widget().destroy()
        canvas2.get_tk_widget().destroy()
        fig1.clear()
        fig2.clear()
        plt.close('all')
        plt.rcdefaults()

        # Clear pyplot internal caches (undocumented but stable)
        try:
            matplotlib._pylab_helpers.Gcf.destroy_all()
        except Exception:
            pass
        check_threshold_window.destroy()

    check_threshold_window.protocol("WM_DELETE_WINDOW", on_closing)

    check_threshold_window.grab_set()
    check_threshold_window.wait_window()
    ap_max_index = np.argmax(sweep_y)
    upper_window = float(upper_entry.get())
    lower_window = float(lower_entry.get())
    
    return decision, upper_window, lower_window
