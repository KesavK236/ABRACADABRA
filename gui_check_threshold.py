import tkinter as tk
import tkinter.font as tkfont
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



def sweep_decrease(check_threshold_window):
    """Handle the event when the user opts to check the previous sweep, setting the decision variable accordingly and closing the window."""
    global decision
    decision = 3
    check_threshold_window.destroy()


def sweep_increase(check_threshold_window):
    """Handle the event when the user opts to check the next sweep, setting the decision variable accordingly and closing the window."""
    global decision
    decision = 2
    check_threshold_window.destroy()



def check_thresh_window(check_thresh, upper_window, lower_window, sweep_x, sweep_y, threshold_index, curr_start_index, current_end_index, file_name=None, sweep_index=None):
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
    file_name : str, optional
        Path of the file being analyzed, shown above the plots.
    sweep_index : int, optional
        Index of the sweep being shown, displayed above the plots.
    
    Returns
    -------
    tuple
        A tuple containing the user's decision (1 for threshold is good, 0 for search in window, 2 for check next sweep, 3 for check previous sweep) and the potentially updated upper and lower bounds of the search window.
    """
    global decision
    global window_width


    if check_thresh == False:
        decision = 1
        return decision, upper_window, lower_window


    check_threshold_window = tk.Toplevel()
    check_threshold_window.title("Check Threshold")
    base_width, base_height = 1284, 800
    check_threshold_window.geometry(f"{base_width}x{base_height}")
    window_width = base_width

    try:   
        icon_path = resource_path("assets/ABRACADABRA.ico")
        check_threshold_window.iconbitmap(icon_path)
    except Exception:
        print("Icon Not found, continuing without it")

    # Shared font objects: reconfiguring their size in on_resize updates every widget using them.
    base_title_size, base_text_size = 16, 12
    base_plot_title_size, base_plot_tick_size = 12, 10
    title_font = tkfont.Font(root=check_threshold_window, family="Verdana", size=base_title_size)
    text_font = tkfont.Font(root=check_threshold_window, family="Verdana", size=base_text_size)

    # Let the plot row and all columns expand so the canvases grow/shrink with the window.
    for col in range(6):
        check_threshold_window.grid_columnconfigure(col, weight=1)
    check_threshold_window.grid_rowconfigure(1, weight=1)

    # Title + "file: sweep n" subtitle stacked in one frame so the rest of the grid keeps its rows.
    title_frame = tk.Frame(check_threshold_window)
    title_frame.grid(column=0, columnspan=6, row=0)
    title_label = tk.Label(title_frame, text="Verify the Calculated Threshold", font=title_font)
    title_label.pack()
    if file_name is not None:
        subtitle = os.path.basename(file_name)
        if sweep_index is not None:
            subtitle += f": sweep {sweep_index}"
        file_label = tk.Label(title_frame, text=subtitle, font=text_font)
        file_label.pack()

    frame_left = tk.Frame(check_threshold_window, highlightbackground="black", highlightthickness=1)
    frame_left.grid(row=1, column=0, columnspan=3, sticky="nsew")

    frame_right = tk.Frame(check_threshold_window, highlightbackground="black", highlightthickness=1)
    frame_right.grid(row=1, column=3, columnspan=3, sticky="nsew")

    for frame in (frame_left, frame_right):
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)


    # 7.5% margin on every side of each plot (right/top are positions, so 1 - border)
    plot_border = 0.075
    fig1, ax1 = plt.subplots()
    fig1.subplots_adjust(left=plot_border, right=1 - plot_border, bottom=plot_border, top=1 - plot_border)
    ax1.plot(sweep_x, sweep_y)
    ax1.plot(sweep_x[threshold_index], sweep_y[threshold_index], 'go')
    ax1.set_title("Standard Trace")

    canvas1 = FigureCanvasTkAgg(fig1, master=frame_left)
    toolbar1 = NavigationToolbar2Tk(canvas1, frame_left)
    toolbar1.update()

    toolbar1.grid(row=0, column=0, sticky="ew")
    canvas1.get_tk_widget().grid(row=1, column=0, sticky="nsew")

    fig2, ax2 = plt.subplots()
    fig2.subplots_adjust(left=plot_border, right=1 - plot_border, bottom=plot_border, top=1 - plot_border)
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
    window_upper_limit_label = tk.Label(check_threshold_window, text="Upper Bound(sec):", font=text_font)
    window_upper_limit_label.grid(column=0, row=2, sticky='e', pady= 5)

    upper_entry = tk.StringVar()
    upper_entry.set(str(upper_window))
    window_upper_limit_entry = tk.Entry(check_threshold_window, width=8, textvariable=upper_entry, font=text_font)
    window_upper_limit_entry.grid(column=1, row=2, sticky= 'w')

    window_lower_limit_label = tk.Label(check_threshold_window, text="Lower Bound (sec):", font=text_font)
    window_lower_limit_label.grid(column=0, row=3, sticky='e')

    lower_entry = tk.StringVar()
    lower_entry.set(str(lower_window))
    window_lower_limit_entry = tk.Entry(check_threshold_window, width=8, textvariable=lower_entry, font=text_font)
    window_lower_limit_entry.grid(column=1, row=3, sticky='w')

    decision = 0
    # Decision buttons
    button_thresh_window = tk.Button(check_threshold_window, text="Search in this window", width=20, height=1, bg="grey", fg="black",
                                    command=lambda: window_button(check_threshold_window), font=text_font)
    button_thresh_window.grid(column=0, columnspan=2, row=4, sticky='s', pady=(5, 10))
    button_thresh_good = tk.Button(check_threshold_window, text="Threshold is good!", width=20, height=1, bg="grey", fg="black",
                                    command=lambda: thresh_good_button(check_threshold_window), font=text_font)
    button_thresh_good.grid(column=2, columnspan=2, row=4, sticky='s', pady=(5, 10))
    button_sweep_decrease = tk.Button(check_threshold_window, text="Check previous sweep", width=20, height=1, bg="grey", fg="black",
                                    command=lambda: sweep_decrease(check_threshold_window), font=text_font)
    button_sweep_decrease.grid(column=4, columnspan=2, row=3, sticky='s', pady=(5, 0))
    button_sweep_increase = tk.Button(check_threshold_window, text="Check next sweep", width=20, height=1, bg="grey", fg="black",
                                    command=lambda: sweep_increase(check_threshold_window), font=text_font)
    button_sweep_increase.grid(column=4, columnspan=2, row=4, sticky='s', pady=(5, 10))



    def on_resize(event):
        """Scale fonts and plot text with the window size (the canvases resize themselves via the grid)."""
        if event.widget is not check_threshold_window:
            return  # <Configure> also fires for every child widget
        width, height = event.width, event.height
        if width <= 1 or height <= 1 or (width, height) == last_size[0]:
            return
        last_size[0] = (width, height)
        # Use the smaller ratio so text never outgrows the space in either direction.
        scale = min(width / base_width, height / base_height)
        title_font.configure(size=max(8, round(base_title_size * scale)))
        text_font.configure(size=max(7, round(base_text_size * scale)))
        for ax in (ax1, ax2):
            ax.title.set_fontsize(max(7, base_plot_title_size * scale))
            ax.tick_params(labelsize=max(6, base_plot_tick_size * scale))
        bottom_pad = max(4, round(10 * scale))
        for button in (button_thresh_window, button_thresh_good, button_sweep_increase):
            button.grid_configure(pady=(bottom_pad // 2, bottom_pad))
        canvas1.draw_idle()
        canvas2.draw_idle()

    last_size = [(base_width, base_height)]
    check_threshold_window.bind("<Configure>", on_resize)

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
