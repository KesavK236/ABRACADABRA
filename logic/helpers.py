import pyabf
# from pynwb import NWBHDF5IO
import numpy as np
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
import os
from hampel import hampel

def load_abf(file_name, sweep_num=0, smooth=False, window_length=25, polyorder=3, loaded=None):
    if loaded == None:
        abf = pyabf.ABF(file_name)
        abf.setSweep(sweep_num)
    else:
        abf = loaded
    sweep_x = np.array(abf.sweepX)
    sweep_y = np.array(abf.sweepY)
    sweep_y_raw = sweep_y
    if smooth:
        sweep_y = savgol_filter(sweep_y, window_length=window_length, polyorder=polyorder)

    sweep_c = np.array(abf.sweepC)
    number_sweeps = num_sweeps(abf)
    x_label = abf.sweepLabelX
    y_label = abf.sweepLabelY
    c_label = abf.sweepLabelC
    sample_rate = abf.sampleRate
    return number_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, x_label, y_label, c_label, loaded, sample_rate


# def load_nwb(file_name, sweep_num=0, smooth=False, window_length=25, polyorder=3, loaded=None):
#     if loaded == None:
#         io = NWBHDF5IO(file_name, 'r')
#         nwbfile = io.read()
#     else:
#         nwbfile = loaded
#     stim_series = list(nwbfile.stimulus.values())[sweep_num]
#     sweep_c = stim_series.data[:]
#     acq_series = list(nwbfile.acquisition.values())[sweep_num]
#     sweep_y = acq_series.data[:]
#     sampling_rate = stim_series.rate
#     max_time = len(sweep_y)/ sampling_rate
#     sweep_x= np.linspace(0, max_time, num=len(sweep_y))
#     number_sweeps = len(list(nwbfile.acquisition.values()))
#     x_label = "Time (s)"
#     y_label = f"Voltage ({acq_series.unit})"
#     c_label = f"Current ({stim_series.unit})"

#     if smooth:
#         sweep_y = savgol_filter(sweep_y, window_length=window_length, polyorder=polyorder)

#     return number_sweeps, sweep_x, sweep_y, sweep_c, x_label, y_label, c_label, loaded

def num_sweeps(abf):
    count = 0
    while True:
        try:
            abf.setSweep(count)
            count += 1
        except ValueError:
            break
    return count

def current_injection_start(sweep_c):
    curr_start_index = 0
    while sweep_c[curr_start_index] == 0:
        curr_start_index += 1
        if curr_start_index >= len(sweep_c):
            curr_start_index = 1
            break
    curr_start_index -= 1
    return curr_start_index

def ap_curr_and_time(sweep_x, sweep_y, sweep_c, sweep_y_d, sweep_x_d, curr_start_index, dvdt):
    j = curr_start_index
    resting_current = sweep_c[j-10]
    ap_bool = 0
    current_threshold = 0
    rheobase = 0
    ap_delay = 0
    threshold_dvdt = int(dvdt)
    # maybe need to add a extra check to ensure this is an action potential
    while j < len(sweep_c) - 1 and ap_bool == 0:
        if sweep_y_d[j] > threshold_dvdt:
            ap_bool = 1
            current_threshold = sweep_c[j]
            rheobase = sweep_c[j] - resting_current
            ap_delay = sweep_x_d[j] - sweep_x[curr_start_index]

        j += 1

    return ap_bool, current_threshold, rheobase, ap_delay

def get_max(sweep_x, sweep_y, max_index, sampling_rate, delta=0.00001):
    lower_bound_index = int((sweep_x[max_index] - delta) * sampling_rate)
    upper_bound_index = int((sweep_x[max_index] + delta) * sampling_rate)
    max_array = sweep_y[lower_bound_index:upper_bound_index]
    peak = np.mean(max_array)
    return peak

def adjust_units(num, figs = 3):
    num = num * 1000
    return round(num, figs)

def no_spaces(name):
    return name.replace(' ', '_')

def check_no_change(sweep_y_d, j, increasing):
    for i in range(10):
        if j + i >= len(sweep_y_d):
            break
        if sweep_y_d[j + i] > 0 and increasing:
            return 0
        elif sweep_y_d[j + i] < 0 and not increasing:
            return 0
    return 1

def save_plot(x, y, xlabel, ylabel, title, filename, folder=None, markers=None):
    plt.clf()
    plt.grid()
    ax = plt.subplot()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.plot(x, y, alpha=0.5)

    if markers:
        for (mx, my, style) in markers:
            ax.plot(mx, my, **style)

    if folder:
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)
    else:
        path = filename

    plt.title(title.split("/")[-1])
    plt.savefig(path)
    return path

def generate_derivatives(sweep_x, sweep_y, hampel_bool=False):
    sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
    sweep_x_d = sweep_x[1:]
    if hampel_bool == True:
        sweep_y_d = hampel(sweep_y_d, window_size=5, n_sigma=3.0).filtered_data

    sweep_y_d2 = np.diff(sweep_y_d) / (1000 * np.diff(sweep_x_d))
    sweep_x_d2 = sweep_x_d[1:]
    return sweep_y_d, sweep_x_d, sweep_y_d2, sweep_x_d2

def is_ramp(filename):
    is_ramp_file = True
    number_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, x_label, y_label, c_label, loaded, sample_rate = load_abf(file_name=filename, sweep_num= 1)
    
    sweep_c_d = np.diff(sweep_c) / (1000 * np.diff(sweep_x))

    curr_start_index = current_injection_start(sweep_c)
    if sweep_c_d[curr_start_index + 500] == 0:
        is_ramp_file = False
    else:
        is_ramp_file = True
    return is_ramp_file

def phase_plane(x, y, yd, f, step):

    if step == "5ms":
        file_name = os.path.basename(f.name)[:-13] + "_5ms_phase_plane"
        title = os.path.basename(f.name)[:-13] + "5ms Phase Plane Plot"

    if step == "1s":
        file_name = os.path.basename(f.name)[:-13] + "_1s_phase_plane"
        title = os.path.basename(f.name)[:-13] + "1s Phase Plane Plot"
    
    table_file = os.path.dirname(f.name) + '\\' + file_name + ".csv"

    with open(table_file, 'w') as g:
        g.write("Time (s), Voltage (mV), dV/dt (mv/ms) \n")
        for i in range(len(yd)):
            g.write(f"{x[i]}, {y[i]}, {yd[i]} \n")
    
    save_plot(y[:-1], yd, "Volage (mV)", "dV/dt (mV/ms)", title, file_name + ".png", folder=os.path.dirname(f.name))

    table_file = os.path.join(os.getcwd(),os.path.dirname(f.name) )

    return table_file