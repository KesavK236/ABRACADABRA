import tkinter as tk
from PIL import ImageTk, Image
import sys
import os
import numpy as np
from logic.helpers import generate_derivatives, save_plot


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def make_scaled_plots(sweep_x, sweep_y, curr_start_index, current_end_index, threshold_index):
    max_index = np.argmax(sweep_y)
    truncated_y = sweep_y[max_index:current_end_index]
    min_index = np.argmin(truncated_y) + max_index
    x = sweep_x[curr_start_index:min_index]
    y = sweep_y[curr_start_index:min_index]

    stand_image_path = save_plot(
        x=x,
        y=y,
        xlabel= "Time (Seconds)",
        ylabel= "Voltage (mV)",
        title= "Threshold of the Trace",
        filename= "imageram\standard.png",
        markers=[(
            [sweep_x[threshold_index]],
            [sweep_y[threshold_index]],
            {
                'marker': "o",
                'markersize': 2,
                'markeredgecolor': 'green',
                'markerfacecolor': 'green'
            }
        )]
    )

    yd, xd, yd2, xd2 = generate_derivatives(x, y)
    adj_thresh_index = threshold_index - curr_start_index
    derivative_image_path = save_plot(
        x=xd,
        y=yd,
        xlabel= "Time (Seconds)",
        ylabel= "Voltage dV/dt (mV/ms)",
        title= "Threshold of Derivative Trace",
        filename= "imageram\derivative.png",
        markers=[(
            [xd[threshold_index-curr_start_index]],
            [yd[threshold_index-curr_start_index]],
            {
                'marker': "o",
                'markersize': 2,
                'markeredgecolor': 'green',
                'markerfacecolor': 'green'
            }
        )]
    )


    return stand_image_path, derivative_image_path

def thresh_good_button(check_threshold_window):
    global decision
    decision = 1
    check_threshold_window.destroy()


def window_button(check_threshold_window):
    global decision
    decision = 0
    check_threshold_window.destroy()



def sweep_increase(check_threshold_window):
    global decision
    decision = 2
    check_threshold_window.destroy()



def check_thresh_window(check_thresh, upper_window, lower_window, sweep_x, sweep_y, threshold_index, curr_start_index, current_end_index):
    global decision

    if check_thresh == False:
        decision = 1
        return decision, upper_window, lower_window


    check_threshold_window = tk.Toplevel()
    check_threshold_window.title("Check Threshold")
    check_threshold_window.geometry("1000x800")
    window_width = 1000

    try:   
        icon_path = resource_path("assets/ABRACADABRA.ico")
        check_thresh_window.iconbitmap(icon_path)
    except Exception:
        print("Icon Not found, continuing without it")

    title_label = tk.Label(check_threshold_window, text="Verify the Calculated Threshold", font=('Verdana', 16))
    title_label.grid(column=0, columnspan=6, row=0)

    standard_img, derivative_img = make_scaled_plots(sweep_x, sweep_y, curr_start_index, current_end_index, threshold_index)

    pil_stand = Image.open(standard_img)
    resize_stand = pil_stand.resize((480, 360), Image.LANCZOS)
    photo_stand = ImageTk.PhotoImage(resize_stand)
    stand_label = tk.Label(check_threshold_window, image=photo_stand)
    stand_label.grid(column=0, columnspan=3, row=1)

    pil_deriv = Image.open(derivative_img)
    resize_deriv = pil_deriv.resize((480, 360), Image.LANCZOS)
    photo_deriv = ImageTk.PhotoImage(resize_deriv)
    deriv_label = tk.Label(check_threshold_window, image=photo_deriv)
    deriv_label.grid(column=3, columnspan=3, row=1)

    # windowed search
    window_upper_limit_label = tk.Label(check_threshold_window, text="Upper Bound(sec):", font=('Verdana', 12))
    window_upper_limit_label.grid(column=0, row=2, sticky='e', pady= 5)

    upper_entry = tk.StringVar()
    upper_entry.set(str(upper_window))
    window_upper_limit_entry = tk.Entry(check_threshold_window, width=5, textvariable=upper_entry, font=('Verdana', 12))
    window_upper_limit_entry.grid(column=1, row=2, sticky= 'w')

    window_lower_limit_label = tk.Label(check_threshold_window, text="Lower Bound (sec):", font=('Verdana', 12))
    window_lower_limit_label.grid(column=0, row=3, sticky='e')

    lower_entry = tk.StringVar()
    lower_entry.set(str(lower_window))
    window_lower_limit_entry = tk.Entry(check_threshold_window, width=5, textvariable=lower_entry, font=('Verdana', 12))
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
        global decision
        decision = 0
        check_threshold_window.destroy()


    check_threshold_window.protocol("WM_DELETE_WINDOW", on_closing)

    check_threshold_window.grab_set()
    check_threshold_window.wait_window()
    ap_max_index = np.argmax(sweep_y)
    upper_window = float(upper_entry.get())
    lower_window = float(lower_entry.get())
    
    return decision, upper_window, lower_window