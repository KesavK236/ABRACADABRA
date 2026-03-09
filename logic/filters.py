import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.signal import butter, filtfilt


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
    """
    Computes rolling mean of x with window size win.

    Parameters
    ----------
    x : 1D numpy array
        The input array.
    win : int
        The window size (odd number).

    Returns
    -------
    1D numpy array
        The rolling mean of x.
    """
    windows = sliding_window_view(x, win)
    means = windows.mean(axis=1)
    # pad ends with NaN or extend nearest value
    return np.concatenate(([means[0]] * (win // 2), means, [means[-1]] * (win // 2)))


def butter_lowpass_filter(x, cutoff_hz, fs_hz, order=4):
    """
    Applies a Butterworth low-pass filter to the input signal x.
    Parameters
    ----------
    x : 1D numpy array
        The input signal to be filtered.
    cutoff_hz : float
        The cutoff frequency of the low-pass filter in Hz.
    fs_hz : float
        The sampling frequency of the input signal in Hz.
    order : int, optional
        The order of the Butterworth filter. Default is 4.
    Returns
    -------
    1D numpy array
        The filtered signal.
    """
    # Normalize cutoff: Wn is relative to Nyquist (fs/2)
    wn = cutoff_hz / (0.5 * fs_hz)
    b, a = butter(order, wn, btype="low")
    return filtfilt(b, a, x)
