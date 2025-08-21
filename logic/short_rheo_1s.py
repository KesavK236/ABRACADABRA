import os
from gui_check_threshold import check_thresh_window
from logic.helpers import load_abf, num_sweeps, current_injection_start, ap_curr_and_time, adjust_units, no_spaces, save_plot, generate_derivatives, is_ramp, phase_plane, get_max
import numpy as np
from scipy.signal import find_peaks
from hampel import hampel

def short_rheo_1s(file_name, f, dvdt, check_threshold):
    num_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, x_label, y_label, c_label, loaded, sample_rate = load_abf(file_name)

    print("Rheo_1s Data:")
    f.write(f"Rheo_1s Data:\n")

    
    curr_start_index = current_injection_start(sweep_c)
   

    
    sweep_index = 0
    threshold_checked = False
    passed_check_func = 0

    while sweep_index < num_sweeps and not threshold_checked:
        num_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, x_label, y_label, c_label, loaded, sample_rate = load_abf(file_name, sweep_num=sweep_index, smooth=True, loaded=loaded)

        sweep_y_d, sweep_x_d, sweep_y_d2, sweep_x_d2 = generate_derivatives(sweep_x, sweep_y, hampel_bool=False)
        
        curr_start_index = current_injection_start(sweep_c)
        current = sweep_c[curr_start_index + 5]
        
        sweep_y_post_curr = sweep_y_raw[curr_start_index:]
        sweep_y_d_post_curr = sweep_y_d[curr_start_index:]
        ap_max = max(sweep_y_post_curr)
        dvdt_max = max(sweep_y_d_post_curr)

        if ap_max >= 0 and dvdt_max >= 0 and current > 0:
            if passed_check_func == 0:
                upper_window = sweep_x[np.argmax(sweep_y_d)]
                lower_window = sweep_x[curr_start_index + int(0.002 * sample_rate)]

            i = int(lower_window * sample_rate)
            
            sweep_y_d, sweep_x_d, sweep_y_d2, sweep_x_d2 = generate_derivatives(sweep_x, sweep_y, hampel_bool=True)


            while (sweep_y_d[i] < dvdt or sweep_y_d2[i] < 15) and sweep_x[i] < upper_window:
                i += 1
            threshold_index = i
            threshold_volt = sweep_y_raw[threshold_index]
            threshold_time = sweep_x[threshold_index] 
            threshold_curr = sweep_c[curr_start_index + 5]

           
            threshold_checked, upper_window, lower_window = check_thresh_window(check_threshold, upper_window, lower_window, sweep_x, sweep_y, threshold_index, curr_start_index, len(sweep_c) - 100)
            passed_check_func = 1
        
        else:
            sweep_index += 1

        if threshold_checked == 2:
            sweep_index += 1
            threshold_checked = 0


    holding_curr = np.mean(sweep_c[curr_start_index-101 : curr_start_index-1])

    curr_end_index = curr_start_index + 1
    length = len(sweep_c)
    while sweep_c[curr_end_index] != 0:
        curr_end_index += 1
        if curr_end_index >= len(sweep_c):
            break
    curr_end_index -= 1

    steady_state_volt = np.mean(sweep_y[curr_end_index - 200 : curr_end_index])

    peaks = find_peaks(sweep_y_post_curr, 0)
    peak_index = peaks[0][0] + curr_start_index
    peak_volt = sweep_y[peak_index]
    filtered_peak_volt = get_max(sweep_x, sweep_y, peak_index, sample_rate)
    peak_time = sweep_x[peak_index]

    # Find the deltas for rising phase
    halfwidth_volt = (peak_volt + threshold_volt) / 2
    rise_delta = peak_volt - threshold_volt
    rise_volt_10 = (rise_delta * .1) + threshold_volt
    rise_volt_90 = (rise_delta * .9) + threshold_volt

    # find the time points of rising phase
    k = threshold_index
    while sweep_y[k] < rise_volt_10:
        k += 1
    rise_time_10 = sweep_x[k]

    while sweep_y[k] < halfwidth_volt:
        k += 1
    halfwidth_start = sweep_x[k]

    while sweep_y[k] < rise_volt_90:
        k += 1
    rise_time_90 = sweep_x[k]

    # find time points of falling phase
    k = peak_index
    while sweep_y[k] > threshold_volt:
        k += 1
    end_fall = sweep_x[k]
    end_fall_index = k
    
    # determine ahp points
    l = k
    # find the nearest steady state point
    while sweep_y_d[l] < 0: 
        l += 1
    if sweep_y[l] < steady_state_volt:
        while sweep_y[l] > steady_state_volt:
            l += 1
        ap_end_index = l
    else:
        while sweep_y_d[l] > 0:
            l += 1
            thing = sweep_x_d[l] * 1000
            thing
        ap_end_index = l

    ahp = 0
    ahp_index = 0
    ahp_array = sweep_y[end_fall_index:ap_end_index]
    ahp_array_raw = sweep_y_raw[end_fall_index:ap_end_index]
    ahp_index = np.argmin(ahp_array)
    ahp = ahp_array_raw[ahp_index]
    ahp_time = sweep_x[ahp_index + end_fall_index]
    fall_delta = ahp - peak_volt
    fall_volt_10 = (fall_delta * .1) + peak_volt
    fall_volt_90 = (fall_delta * .9) + peak_volt
    ahp_halfwidth_volt = (steady_state_volt + ahp) / 2

    # find falling phase time points
    k = peak_index
    while sweep_y[k] > fall_volt_10:
        k += 1
    fall_time_10 = sweep_x[k]

    while sweep_y[k] > halfwidth_volt:
        k += 1
    halfwidth_end = sweep_x[k]

    while sweep_y[k] > fall_volt_90:
        k += 1
    fall_time_90 = sweep_x[k]

    # Find AHP time points
    k = peak_index
    while sweep_y[k] > ahp_halfwidth_volt:
        k +=1
    ahp_halfwidth_start = sweep_x[k]

    k = ahp_index
    while sweep_y[k] < ahp_halfwidth_volt:
        k += 1
    ahp_halfwidth_end = sweep_x[k]

    rise_time_raw = adjust_units((peak_time - threshold_time))
    rise_time_10_90 = adjust_units((rise_time_90 - rise_time_10))
    fall_time_raw = adjust_units((ahp_time - peak_time))
    fall_time_10_90 = adjust_units((fall_time_90 - fall_time_10))
    halfwidth = adjust_units((halfwidth_end - halfwidth_start))
    ahp_halfwidth = adjust_units((ahp_halfwidth_start - ahp_halfwidth_end))
    rheobase = threshold_curr - holding_curr
    curr_start_time = sweep_x[curr_start_index]
    relative_thresh_time = adjust_units((threshold_time-curr_start_time))
    relative_peak_time = adjust_units((peak_time-curr_start_time))

    # Store values and output
    print(f"Relative Rheobase (nA): {rheobase}")
    print(f"Current start time: {curr_start_time}")
    f.write(f"Relative Rheobase (nA):, {rheobase}\n")

    print(f"AP Peak (mV): {filtered_peak_volt}")
    f.write(f"AP Peak (mV):, {filtered_peak_volt}\n")

    print(f"AP Amplitude (mV): {filtered_peak_volt - threshold_volt}")
    f.write(f"AP Amplitude (mV):, {filtered_peak_volt - threshold_volt}\n")

    print(f"Time of Peak (ms): {relative_peak_time}")
    print(f"Raw Peak Time: {peak_time}")
    f.write(f"Time of Peak (ms):, {relative_peak_time}\n")

    print(f"AP Voltage Threshold (mV): {threshold_volt}")
    f.write(f"AP Voltage Threshold (mV):, {threshold_volt}\n")

    print(f"Time of Threshold (ms): {relative_thresh_time}")
    print(f"Raw Thresh Time: {threshold_time}")
    f.write(f"Time of Threshold (ms):, {relative_thresh_time}\n")

    print(f"AP Rise Time Raw (ms): {rise_time_raw}")
    f.write(f"AP Rise Time Raw (ms):, {rise_time_raw}\n")

    print(f"AP Rise Time 10-90 (ms): {rise_time_10_90}")
    f.write(f"AP Rise Time 10-90 (ms):, {rise_time_10_90}\n")

    print(f"AP Halfwidth (ms): {halfwidth}")
    f.write(f"AP Halfwidth (ms):, {halfwidth}\n")

    print(f"AP Falling Time Raw (ms): {fall_time_raw}")
    f.write(f"AP Falling Time Raw (ms):, {fall_time_raw}\n")

    print(f"AP Falling Time 10-90 (ms): {fall_time_10_90}")
    f.write(f"AP Falling Time 10-90 (ms):, {fall_time_10_90}\n")

    print(f"AHP Minimum (mV): {ahp}")
    f.write(f"AHP Minimum (mV):, {ahp}\n")

    print(f"AHP Relative (mV): {ahp - threshold_volt}")
    f.write(f"AHP Relative (mV):, {ahp - threshold_volt}\n")

    print(f"AHP half-width (ms): {ahp_halfwidth}")
    f.write(f"AHP half-width (ms):, {ahp_halfwidth}\n")

    print(f"Upstroke-Downstroke ratio: {rise_time_10_90 / fall_time_10_90}")
    f.write(f"Upstroke-Downstroke ratio:, {rise_time_10_90 / fall_time_10_90}\n")

    image_name = no_spaces(f.name[:-4]) + "_rheo_1s_graph.png"
    save_plot(
        x=sweep_x,
        y= sweep_y,
        xlabel= x_label,
        ylabel= y_label,
        title= os.path.basename(image_name)[:-4],
        filename=image_name,
        folder=os.path.dirname(f.name)
    )

    phase_plane_table = phase_plane(sweep_x, sweep_y_raw, sweep_y_d, f, step="1s")

    return phase_plane_table