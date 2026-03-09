import numpy as np
import pyabf
from hampel import hampel
from scipy.signal import find_peaks, savgol_filter

from .filters import butter_lowpass_filter, rolling_mean


def load_abf(
    file_name=None,
    sweep_num=0,
    smooth=False,
    window_length=25,
    polyorder=3,
    loaded=None,
    protocol="rheo",
    current_record=-1,
):
    """
    Loads the ABF into arrays and features depending on sweep index.

    Parameters
    ----------
    file_name : str
        The filepath of the ABF file.
    sweep_num : int, optional
        The index of the sweep to extract. Default is 0.
    smooth : bool, optional
        If True, the voltage sweep will be filtered with a Savitzky-Golay filter.
        If False (default), the voltage sweep will not be filtered.
    window_length : int, optional
        The length of the window for the Savitzky-Golay filter. Default is 25.
    polyorder : int, optional
        The polynomial order for the Savitzky-Golay filter. Default is 3.
    loaded : ABF object, optional
        A pre-loaded ABF object (e.g., `pyabf.ABF`). Default is None, meaning the
        file will be loaded fresh.

    Returns
    -------
    tuple
        A tuple containing the following:

        number_sweeps : int
            The number of sweeps in the ABF.
        sweep_x : array-like of float
            Time points of the given sweep.
        sweep_y : array-like of float
            Voltage points of the given sweep. Optionally filtered.
        sweep_y_raw : array-like of float
            Unfiltered voltage points of the given sweep.
        sweep_c : array-like of float
            The recorded current points of the given sweep.
        sweep_stim : array-like of float
            The stimulus current points from the epoch protocol of the given sweep.
        x_label : str
            Units of the time sweep.
        y_label : str
            Units of the voltage sweep.
        c_label : str
            Units of the current sweep.
        loaded : ABF object
            The loaded ABF object.
        sample_rate : int
            The sample rate of the ABF recording.
    """

    if loaded is None:
        abf = pyabf.ABF(file_name)
    else:
        abf = loaded
    number_sweeps = num_sweeps(abf)
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
    sweep_c = np.array(abf.sweepC)
    c_label = abf.sweepLabelC
    current_units = abf.sweepUnitsC
    if current_record == -1:
        try:
            peaks = verify_current(abf, number_sweeps)

            if protocol == "rheo" and peaks != 2 and peaks != -1:
                raise Exception("Channel 1 isn't current")
            if protocol == "ramp" and peaks != 1 and peaks != -1:
                raise Exception("Channel 1 isn't current")
            abf.setSweep(sweep_num, channel=1)
            sweep_c = np.array(abf.sweepY)
            c_label = abf.sweepLabelY
            current_units = abf.sweepUnitsY
            current_record = 1
            if "(nA)" and "(pA)" not in c_label:
                raise Exception("Channel 1 isn't current")
        except Exception:
            abf.setSweep(sweep_num, channel=0)
            sweep_c = np.array(abf.sweepC)
            c_label = abf.sweepLabelC
            current_record = 0
    elif current_record == 1:
        abf.setSweep(sweep_num, channel=1)
        sweep_c = np.array(abf.sweepY)
        c_label = abf.sweepLabelY
        current_units = abf.sweepUnitsY
    else:
        abf.setSweep(sweep_num, channel=0)
        sweep_c = np.array(abf.sweepC)
        c_label = abf.sweepLabelC
        current_units = abf.sweepUnitsC

    sample_rate = abf.sampleRate

    return (
        number_sweeps,
        sweep_x,
        sweep_y,
        sweep_y_raw,
        sweep_c,
        sweep_stim,
        x_label,
        y_label,
        c_label,
        loaded,
        sample_rate,
        current_units,
        current_record,
    )


def verify_current(abf, number_sweeps):
    """Verify whether the current is recorded in Channel 1 or to use the epoch table for current.
    Parameters
    ----------
    abf : ABF object
        The loaded ABF object.
    number_sweeps : int
        The number of sweeps in the ABF.
    Returns
    -------
    int
        The number of peaks in the current derivative sweep, or -1 if an error occurs.
    """
    sample_rate = abf.dataRate
    sweep_num = number_sweeps - 1
    abf.setSweep(sweep_num, channel=0)
    sweep_x = np.array(abf.sweepX)
    abf.setSweep(sweep_num, channel=1)
    sweep_c = np.array(abf.sweepY)
    didt = np.gradient(sweep_c, sweep_x * 1000)
    min_idx = np.argmin(didt)
    adidt = abs(didt)
    adidt_peaks, adidt_props = find_peaks(adidt, 500)
    adidt_heights = adidt_props["peak_heights"]
    min_index = np.where(adidt_peaks == min_idx)[0][0]
    _ = adidt_peaks[:min_index]

    refractory_period = 0.001 * sample_rate
    peak_set = set()
    peak_set.add(adidt_peaks[len(adidt_peaks) - 1])
    last_added = adidt_peaks[len(adidt_peaks) - 1]
    last_added_value = adidt_heights[len(adidt_peaks) - 1]
    for i in range(len(adidt_peaks) - 2, -1, -1):
        if last_added - adidt_peaks[i] < refractory_period:
            if last_added_value < adidt_heights[i]:
                peak_set.discard(last_added)
                peak_set.add(adidt_peaks[i])
                last_added = adidt_peaks[i]
                last_added_value = adidt_heights[i]
        else:
            peak_set.add(adidt_peaks[i])
            last_added = adidt_peaks[i]
            last_added_value = adidt_heights[i]

    return len(peak_set)


def num_sweeps(abf):
    return abf.sweepCount


def current_injection_points_rheo(abf, sample_rate, sweep_ind, sweep_x, sweep_c, units="pA"):
    """
    Identifies the start and end indices of current injection in a Rheo protocol sweeps.
    Parameters
    ----------
    abf : ABF object
        The loaded ABF object.
    sample_rate : float
        The sampling rate of the ABF recording in Hz.
    sweep_ind : int
        The index of the sweep being analyzed.
    sweep_x : 1D numpy array
        The time points of the sweep in seconds.
    sweep_c : 1D numpy array
        The current values of the sweep in pA or nA.
    units : str, optional
        The units of the current values ("pA" or "nA"). Default is "pA".
    Returns
    -------
    tuple
        A tuple containing:
        - curr_start_index (int): The index where current injection starts.
        - curr_end_index (int): The index where current injection ends.
        - holding_curr (float): The average holding current before injection.
        - stim_curr (float): The average stimulus current during injection.
    """
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
            _, _, _, _, sweep_c, _, _, _, _, _, _, _, _ = load_abf(sweep_num=sweep_ind + 1, loaded=abf)
        except Exception:
            _, _, _, _, sweep_c, _, _, _, _, _, _, _, _ = load_abf(sweep_num=sweep_ind - 1, loaded=abf)
        sweep_c = butter_lowpass_filter(sweep_c, cutoff_hz=5000, fs_hz=sample_rate, order=4)
        sweep_c_base_smooth = savgol_filter(sweep_c, window_length=100, polyorder=3)

    dadt = np.diff(sweep_c) / (1000 * np.diff(sweep_x))

    min_idx = np.argmin(dadt)
    max_idx = np.argmax(dadt)
    if min_idx < max_idx:
        curr_start_index = min_idx
        curr_end_index = max_idx - 1
    else:
        curr_start_index = max_idx
        curr_end_index = min_idx - 1
    if zero_sweep_bool:
        sweep_c = sweep_c_stored
    holding_curr = np.mean(sweep_c[100 : curr_start_index - 100])
    stim_curr = np.mean(sweep_c[curr_start_index + 10 : curr_end_index - 10])

    return curr_start_index, curr_end_index, holding_curr, stim_curr


def current_injection_points_ramp(abf, sample_rate, sweep_ind, sweep_x, sweep_c, sweep_stim, units="pA"):
    """
    Identifies the start and end indices of current injection in a Ramp protocol sweeps.
    Parameters
    ----------
    abf : ABF object
        The loaded ABF object.
    sample_rate : float
        The sampling rate of the ABF recording in Hz.
    sweep_ind : int
        The index of the sweep being analyzed.
    sweep_x : 1D numpy array
        The time points of the sweep in seconds.
    sweep_c : 1D numpy array
        The current values of the sweep in pA or nA.
    units : str, optional
        The units of the current values ("pA" or "nA"). Default is "pA".
    Returns
    -------
    tuple
        A tuple containing:
        - curr_start_index (int): The index where current injection starts.
        - curr_end_index (int): The index where current injection ends.
        - holding_curr (float): The average holding current before injection.
        - stim_curr (float): The average stimulus current during injection.
    """
    _ = units
    zero_sweep_bool = False
    stim_diff = np.abs(np.max(sweep_stim) - np.min(sweep_stim))
    if stim_diff <= 0:
        try:
            _, _, _, _, _, sweep_stim, _, _, _, _, _, _, _ = load_abf(sweep_num=sweep_ind + 1, loaded=abf)
        except IndexError:
            _, _, _, _, _, sweep_stim, _, _, _, _, _, _, _ = load_abf(sweep_num=sweep_ind - 1, loaded=abf)

    sweep_c_base_smooth = savgol_filter(sweep_c, window_length=25, polyorder=3)
    sweep_c_roll_mean = rolling_mean(sweep_c_base_smooth, win=1001)

    diff = np.abs(np.max(sweep_c_roll_mean) - np.min(sweep_c_roll_mean))
    if diff < 1.5:
        zero_sweep_bool = True
        sweep_c_stored = sweep_c
        try:
            _, _, _, _, sweep_c, _, _, _, _, _, _, _, _ = load_abf(sweep_num=sweep_ind + 1, loaded=abf)
        except Exception:
            _, _, _, _, sweep_c, _, _, _, _, _, _, _, _ = load_abf(sweep_num=sweep_ind - 1, loaded=abf)
        sweep_c = butter_lowpass_filter(sweep_c, cutoff_hz=5000, fs_hz=sample_rate, order=4)
        sweep_c_base_smooth = savgol_filter(sweep_c, window_length=25, polyorder=3)
        sweep_c_roll_mean = rolling_mean(sweep_c_base_smooth, win=1001)

    _ = sweep_c_roll_mean
    stim_didt = np.gradient(sweep_stim)
    didt_min = np.argmin(stim_didt)
    didt_max = np.argmax(stim_didt)
    i = 0
    while sweep_stim[i] == 0:
        i += 1
    stim_start = sweep_x[i]
    _ = stim_start
    if didt_max < didt_min:
        stim_end = sweep_x[didt_min]
    else:
        stim_end = sweep_x[didt_max]
    stim_length = stim_end - sweep_x[i]

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


def ap_curr_and_time(
    sweep_x, sweep_y, sweep_c, sweep_y_d, sweep_x_d, curr_start_index, curr_end_indx, dvdt, sample_rate
):
    """Determines the current, voltage, and time of threshold if an action potential occured
    Parameters
    ----------
    sweep_x : 1D numpy array
        The time points of the sweep in seconds.
    sweep_y : 1D numpy array
        The voltage values of the sweep in mV.
    sweep_c : 1D numpy array
        The current values of the sweep in pA or nA.
    sweep_y_d : 1D numpy array
        The first derivative of the voltage sweep.
    sweep_x_d : 1D numpy array
        The time points corresponding to the first derivative of the voltage sweep.
    curr_start_index : int
        The index where current injection starts.
    curr_end_indx : int
        The index where current injection ends.
    dvdt : float
        The threshold for the first derivative to determine if an action potential occurred.
    sample_rate : float
        The sampling rate of the ABF recording in Hz.
    Returns
    -------
    tuple
        A tuple containing:
        - ap_bool (bool): Whether an action potential was detected.
        - current_threshold (float): The current at which the action potential threshold was crossed.
        - rheobase (float): The difference between the current threshold and the holding current.
        - ap_delay (float): The time delay from the start of current injection to the action potential threshold crossing.
        - voltage_threshold (float): The voltage at which the action potential threshold was crossed.
    """
    j = curr_start_index
    resting_current = sweep_c[j - 10]
    ap_bool = 0
    current_threshold = 0
    rheobase = 0
    ap_delay = 0
    threshold_dvdt = int(dvdt)
    voltage_threshold = 0
    _ = int(0.002 * sample_rate)
    # maybe need to add a extra check to ensure this is an action potential
    while j < curr_end_indx and ap_bool == 0:
        if sweep_y_d[j] > threshold_dvdt:
            ap_bool = 1
            current_threshold = sweep_c[j]
            rheobase = sweep_c[j] - resting_current
            ap_delay = sweep_x_d[j] - sweep_x[curr_start_index]
            voltage_threshold = sweep_y[j]

        j += 1

    return ap_bool, current_threshold, rheobase, ap_delay, voltage_threshold


def get_max(sweep_x, sweep_y, max_index, sampling_rate, delta=0.00001):
    """Calulates the maximum voltage of the action potential by taking the mean of the voltage values around the peak to account for noise.
    Parameters
    ----------
    sweep_x : 1D numpy array
        The time points of the sweep in seconds.
    sweep_y : 1D numpy array
        The voltage values of the sweep in mV.
    max_index : int
        The index of the peak of the action potential.
    sampling_rate : float
        The sampling rate of the ABF recording in Hz.
    delta : float, optional
        The time window in seconds around the peak to average for the maximum voltage calculation. Default is 0.00001 seconds (10 ms).
    Returns
    -------
    float
        The calculated maximum voltage of the action potential.
    """
    lower_bound_index = int((sweep_x[max_index] - delta) * sampling_rate)
    upper_bound_index = int((sweep_x[max_index] + delta) * sampling_rate)
    max_array = sweep_y[lower_bound_index:upper_bound_index]
    peak = np.mean(max_array)
    return peak


def generate_derivatives(sweep_x, sweep_y, hampel_bool=False):
    """Generates the first and second derivatives of the voltage sweep.
    Parameters
    ----------
    sweep_x : 1D numpy array
        The time points of the sweep in seconds.
    sweep_y : 1D numpy array
        The voltage values of the sweep in mV.
    hampel_bool : bool, optional
        Whether to apply a Hampel filter to the first derivative to remove outliers. Default is False.
    Returns
    -------
    tuple
        A tuple containing:
        - sweep_y_d (1D numpy array): The first derivative of the voltage sweep.
        - sweep_x_d (1D numpy array): The time points corresponding to the first derivative of the voltage sweep.
        - sweep_y_d2 (1D numpy array): The second derivative of the voltage sweep
        - sweep_x_d2 (1D numpy array): The time points corresponding to the second derivative of the voltage sweep.
        """
    sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
    sweep_x_d = sweep_x[1:]
    if hampel_bool is True:
        sweep_y_d = hampel(sweep_y_d, window_size=5, n_sigma=3.0).filtered_data

    sweep_y_d2 = np.diff(sweep_y_d) / (1000 * np.diff(sweep_x_d))
    sweep_x_d2 = sweep_x_d[1:]
    return sweep_y_d, sweep_x_d, sweep_y_d2, sweep_x_d2


def is_ramp(filename):
    """Determines whether the given ABF file is a Ramp protocol by checking for a change in the stimulus current.
    Parameters
    ----------
    filename : str
        The filepath of the ABF file to check.
    Returns
    -------
    bool
        True if the file is a Ramp protocol, False otherwise.
    """
    is_ramp_file = True
    sweep_num = 1
    _, sweep_x, _, _, _, sweep_stim, _, _, _, loaded, _, _, _ = load_abf(file_name=filename, sweep_num=sweep_num)

    max_current = np.max(sweep_stim)
    min_current = np.min(sweep_stim)
    while max_current == 0 and min_current == 0:
        _, sweep_x, _, _, _, sweep_stim, _, _, _, loaded, _, _, _ = load_abf(
            file_name=filename, sweep_num=sweep_num + 1, loaded=loaded
        )
        max_current = np.max(sweep_stim)

    sweep_stim_d = np.gradient(sweep_stim)
    i = 0
    while sweep_stim[i] == 0 and i < len(sweep_stim):
        i += 1

    if sweep_stim_d[i + 500] == 0:
        is_ramp_file = False
    else:
        is_ramp_file = True
    return is_ramp_file
