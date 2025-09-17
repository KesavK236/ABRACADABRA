import pyabf
# from pynwb import NWBHDF5IO
import numpy as np
from scipy.signal import savgol_filter, butter, filtfilt
import matplotlib.pyplot as plt
import os
from hampel import hampel
from numpy.lib.stride_tricks import sliding_window_view

def load_abf(file_name=None, sweep_num=0, smooth=False, window_length=25, polyorder=3, loaded=None):
    if loaded == None:
        abf = pyabf.ABF(file_name)
    else:
        abf = loaded
    abf.setSweep(sweep_num, channel=0)
    loaded = abf
    sweep_x = np.array(abf.sweepX)
    sweep_y = np.array(abf.sweepY)
    sweep_y_raw = sweep_y
    sweep_stim = np.array(abf.sweepC)
    if smooth:
        sweep_y = savgol_filter(sweep_y, window_length=window_length, polyorder=polyorder)
    x_label = abf.sweepLabelX
    y_label = abf.sweepLabelY

    abf.setSweep(sweep_num, channel=1)
    sweep_c = np.array(abf.sweepY)
    number_sweeps = num_sweeps(abf)
    c_label = abf.sweepLabelY
    sample_rate = abf.sampleRate
    return number_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, sweep_stim, x_label, y_label, c_label, loaded, sample_rate


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
    return abf.sweepCount

def std_threshold_smoother(x, win=51, std_thresh=50):
    """
    Smooths toward local mean if the window is stable.
    
    x          : 1D numpy array
    win        : window size (odd number)
    std_thresh : maximum std allowed to apply smoothing
    
    Returns a new 1D array.
    """
    if win % 2 == 0:
        raise ValueError("win must be odd")
    half = win // 2
    n = len(x)
    y = np.copy(x)
    
    for i in range(n):
        lo = max(0, i - half)
        hi = min(n, i + half + 1)
        seg = x[lo:hi]
        if np.std(seg) <= std_thresh:
            y[i] = np.mean(seg)  # flatten small variation
        # else: keep original (preserve big shifts)
    return y

def rolling_mean(x, win):
    # x: 1D numpy array
    # win: window size
    windows = sliding_window_view(x, win)
    means = windows.mean(axis=1)
    # pad ends with NaN or extend nearest value
    return np.concatenate(([means[0]]*(win//2), means, [means[-1]]*(win//2)))

def butter_lowpass_filter(x, cutoff_hz, fs_hz, order=4):
    # Normalize cutoff: Wn is relative to Nyquist (fs/2)
    wn = cutoff_hz / (0.5 * fs_hz)
    b, a = butter(order, wn, btype="low")
    return filtfilt(b, a, x)


def current_injection_points_rheo(abf, sample_rate, sweep_ind, sweep_x, sweep_c, units="pA"):    
    if units == "nA":
        sweep_c = sweep_c * 1e3
    elif units == "A":
        sweep_c = sweep_c * 1e12
    zero_sweep_bool = False
    sweep_c = butter_lowpass_filter(sweep_c, cutoff_hz=5000, fs_hz=sample_rate, order=4)
    sweep_c_base_smooth = savgol_filter(sweep_c, window_length=100, polyorder=3)
    sweep_c_roll_mean = rolling_mean(sweep_c_base_smooth, win=1001)

    diff = np.abs(np.max(sweep_c_roll_mean) - np.min(sweep_c_roll_mean))
    if diff < 1.5:
        zero_sweep_bool = True
        sweep_c_stored = sweep_c
        try:
            _, _, _, _, sweep_c, _, _, _, _, _, _ = load_abf(sweep_num=sweep_ind + 1, loaded=abf)
        except:
            _, _, _, _, sweep_c, _, _, _, _, _, _ = load_abf(sweep_num=sweep_ind - 1, loaded=abf)
        sweep_c = butter_lowpass_filter(sweep_c, cutoff_hz=5000, fs_hz=sample_rate, order=4)
        sweep_c_base_smooth = savgol_filter(sweep_c, window_length=100, polyorder=3)

    curr_start_index = 0
    dadt = np.diff(sweep_c) / (1000 * np.diff(sweep_x))
    
    min = np.argmin(dadt)
    max = np.argmax(dadt)
    if min < max:
        curr_start_index = min
        curr_end_index = max
    else:
        curr_start_index = max
        curr_end_index = min
    if zero_sweep_bool:
        sweep_c = sweep_c_stored
    holding_curr = np.mean(sweep_c[curr_start_index - 1000 : curr_start_index - 1])
    middle_index = (curr_start_index + curr_end_index) // 2
    stim_curr = np.mean(sweep_c[middle_index - 500 : middle_index + 500])
    
    return curr_start_index, curr_end_index, holding_curr, stim_curr

def current_injection_points_ramp(abf, sample_rate, sweep_ind, sweep_x, sweep_c, sweep_stim, units="pA"):
    zero_sweep_bool = False
    stim_diff = np.abs(np.max(sweep_stim) - np.min(sweep_stim))
    if stim_diff < 1.5:
        try:
            _, _, _, _, _, sweep_stim, _, _, _, _, _ = load_abf(sweep_num=sweep_ind + 1, loaded=abf)
        except IndexError:
            _, _, _, _, _, sweep_stim, _, _, _, _, _ = load_abf(sweep_num=sweep_ind - 1, loaded=abf)

    sweep_c_base_smooth = savgol_filter(sweep_c, window_length=25, polyorder=3)
    sweep_c_roll_mean = rolling_mean(sweep_c_base_smooth, win=1001)

    diff = np.abs(np.max(sweep_c_roll_mean) - np.min(sweep_c_roll_mean))
    if diff < 1.5:
        zero_sweep_bool = True
        sweep_c_stored = sweep_c
        try:
            _, _, _, _, sweep_c, _, _, _, _, _, _ = load_abf(sweep_num=sweep_ind + 1, loaded=abf)
        except:
            _, _, _, _, sweep_c, _, _, _, _, _, _ = load_abf(sweep_num=sweep_ind - 1, loaded=abf)
        sweep_c = butter_lowpass_filter(sweep_c, cutoff_hz=5000, fs_hz=sample_rate, order=4)
        sweep_c_base_smooth = savgol_filter(sweep_c, window_length=25, polyorder=3)
        sweep_c_roll_mean = rolling_mean(sweep_c_base_smooth, win=1001)


    stim_didt = np.gradient(sweep_stim)
    didt_min = np.argmin(stim_didt)
    didt_max = np.argmax(stim_didt)
    i = 0
    while sweep_stim[i] == 0:
        i += 1
    stim_start = sweep_x[i]
    stim_start_index = i
    if didt_max < didt_min:
        stim_end = sweep_x[didt_min]
        stim_end_index = didt_min
    else:
        stim_end = sweep_x[didt_max]
        stim_end_index = didt_max
    stim_length = stim_end - stim_start
    

    sample_rate = abf.dataRate
    didt = np.gradient(sweep_c, sweep_x)
    current_end_index = np.argmin(didt)
    current_end_time = sweep_x[current_end_index]

    current_start_time = current_end_time - stim_length
    current_start_index = int(current_start_time * sample_rate)
    
    if zero_sweep_bool:
        sweep_c = sweep_c_stored

    holding_curr = np.mean(sweep_c[current_start_index - 500 : current_start_index - 1])
    stim_curr = np.mean(sweep_c[current_end_index - 100 : current_end_index - 1])

    return current_start_index, current_end_index, holding_curr, stim_curr

def ap_curr_and_time(sweep_x, sweep_y, sweep_c, sweep_y_d, sweep_x_d, curr_start_index, curr_end_indx, dvdt):
    j = curr_start_index
    resting_current = sweep_c[j-10]
    ap_bool = 0
    current_threshold = 0
    rheobase = 0
    ap_delay = 0
    threshold_dvdt = int(dvdt)
    # maybe need to add a extra check to ensure this is an action potential
    while j < curr_end_indx and ap_bool == 0:
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
    number_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, sweep_stim, x_label, y_label, c_label, loaded, sample_rate = load_abf(file_name=filename, sweep_num= 1)
    
    sweep_c_d = np.diff(sweep_c) / (1000 * np.diff(sweep_x))

    curr_start_index, curr_end_index = current_injection_points_rheo(sweep_c)
    if sweep_c_d[curr_start_index + 500] == 0:
        is_ramp_file = False
    else:
        is_ramp_file = True
    return is_ramp_file

def phase_plane(x, y, yd, df, step, output_dir):

    dfname = df.index[0]
    if step == "5ms":
        file_name = dfname + "_5ms_phase_plane"
        title = dfname + "5ms Phase Plane Plot"

    if step == "1s":
        file_name = dfname+ "_1s_phase_plane"
        title = dfname+ "1s Phase Plane Plot"
    
    table_file = os.path.join(output_dir, file_name + ".csv" )

    with open(table_file, 'w') as g:
        g.write("Time (s), Voltage (mV), dV/dt (mv/ms) \n")
        for i in range(len(yd)):
            g.write(f"{x[i]}, {y[i]}, {yd[i]} \n")
    
    save_plot(y[:-1], yd, "Volage (mV)", "dV/dt (mV/ms)", title, file_name + ".png", folder=os.path.dirname(table_file))

    return table_file