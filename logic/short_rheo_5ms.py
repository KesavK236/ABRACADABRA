import os
from gui_check_threshold import check_thresh_window
from logic.helpers import load_abf, current_injection_points_rheo, ap_curr_and_time, adjust_units, no_spaces, save_plot, generate_derivatives, is_ramp, phase_plane, get_max
import numpy as np
from scipy.signal import savgol_filter, find_peaks


def short_rheo_5ms(file_name, df, dvdt=20, check_threshold=False, output_dir=os.getcwd()):
    num_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, __,  x_label, y_label, c_label, loaded, sample_rate = load_abf(file_name)

    print("Rheo_5ms Data:")
    # f.write(f"Rheo_5ms Data:\n")


    curr_start_index, curr_end_index, holding_curr, stim_curr = current_injection_points_rheo(loaded, sample_rate, 0, sweep_x, sweep_c)
   

    
    sweep_index = 0
    threshold_checked = False
    passed_check_func = 0

    while sweep_index < num_sweeps and not threshold_checked:
        num_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, __, x_label, y_label, c_label, loaded, sample_rate = load_abf(file_name, sweep_num=sweep_index, smooth=True, loaded=loaded)

        sweep_y_d, sweep_x_d, sweep_y_d2, sweep_x_d2 = generate_derivatives(sweep_x, sweep_y, hampel_bool=False)
        
        curr_start_index, curr_end_index, holding_curr, stim_curr = current_injection_points_rheo(loaded, sample_rate, 0, sweep_x, sweep_c)
        sweep_y_post_curr = sweep_y_raw[curr_start_index:]
        sweep_y_d_post_curr = sweep_y_d[curr_start_index:]
        ap_max = max(sweep_y_post_curr)
        dvdt_max = max(sweep_y_d_post_curr)

        if ap_max >= 0:
            if passed_check_func == 0:
                upper_window = sweep_x[np.argmax(sweep_y_d)]
                lower_window = sweep_x[curr_start_index + int(0.002 * sample_rate)]

            i = int(upper_window * sample_rate)
            
            sweep_y_d, sweep_x_d, sweep_y_d2, sweep_x_d2 = generate_derivatives(sweep_x, sweep_y, hampel_bool=True)

            while (sweep_y_d[i] >= dvdt or sweep_y_d2[i] < 10 ) and sweep_x[i] > lower_window:
                i -= 1
            threshold_index = i
            threshold_volt = sweep_y_raw[threshold_index]
            threshold_time = sweep_x[threshold_index] 

           
            threshold_checked, upper_window, lower_window = check_thresh_window(check_threshold, upper_window, lower_window, sweep_x, sweep_y, threshold_index, curr_start_index, len(sweep_c) - 100)
            passed_check_func = 1
        
        else:
            sweep_index += 1

        if threshold_checked == 2:
            sweep_index += 1
            threshold_checked = 0


    holding_curr = np.mean(sweep_c[curr_start_index-101 : curr_start_index-1])

    steady_state_volt = np.mean(sweep_y[len(sweep_c) - 200 : len(sweep_c)])


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
        ap_end_index = l

    ahp = 0
    ahp_index = 0
    ahp_array = sweep_y[end_fall_index:ap_end_index]
    ahp_index = np.argmin(ahp_array)
    ahp = ahp_array[ahp_index]
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

    rise_time_raw = peak_time - threshold_time
    rise_time_10_90 = rise_time_90 - rise_time_10
    fall_time_raw = end_fall - peak_time
    fall_time_10_90 = fall_time_90 - fall_time_10
    halfwidth = halfwidth_end - halfwidth_start
    ahp_halfwidth = ahp_halfwidth_start - ahp_halfwidth_end
    rheobase = stim_curr - holding_curr

    # Format values
    rise_time_raw = adjust_units(rise_time_raw)
    rise_time_10_90 = adjust_units(rise_time_10_90)
    halfwidth = adjust_units(halfwidth)
    fall_time_raw = adjust_units(fall_time_raw)
    fall_time_10_90 = adjust_units(fall_time_10_90)
    ahp_halfwidth = adjust_units(ahp_halfwidth)
    curr_start_time = sweep_x[curr_start_index]
    relative_thresh_time = adjust_units((threshold_time-curr_start_time))
    relative_peak_time = adjust_units((peak_time-curr_start_time))

    # Store values and output
    if "(nA)" in c_label:
        current_units = "nA"
    elif "(pA)" in c_label:
        current_units = "pA"
    print(f"Holding Current ({current_units}): {holding_curr}")
    df[f"Holding Current 1s ({current_units})"] = holding_curr

    print(f"Rheobase ({current_units}): {stim_curr}")
    df[f"Rheobase 1s ({current_units})"] = stim_curr

    print(f"Relative Rheobase ({current_units}): {rheobase}")
    df[f"Relative Rheobase 1s ({current_units})"] = rheobase
    print(f"Current start time: {curr_start_time}")

    print(f"AP Peak (mV): {filtered_peak_volt}")
    df["AP Peak 5ms (mV)"] = filtered_peak_volt

    print(f"AP Amplitude (mV): {filtered_peak_volt - threshold_volt}")
    df["AP Amplitude 5ms (mV)"] = filtered_peak_volt - threshold_volt

    print(f"Time of Peak (ms): {relative_peak_time}")
    print(f"Raw Peak Time: {peak_time}")
    df["Time of Peak 5ms (ms)"] = relative_peak_time

    print(f"AP Voltage Threshold (mV): {threshold_volt}")
    df["AP Voltage Threshold 5ms (mV)"] = threshold_volt

    print(f"Time of Threshold (ms): {relative_thresh_time}")
    print(f"Raw Thresh Time: {threshold_time}")
    df["Time of Threshold 5ms (ms)"] =  relative_thresh_time

    print(f"AP Rise Time Raw (ms): {rise_time_raw}")
    df["AP Rise Time Raw 5ms (ms)"] = rise_time_raw

    print(f"AP Rise Time 10-90 (ms): {rise_time_10_90}")
    df["AP Rise Time 10-90 5ms (ms)"]  = rise_time_10_90

    print(f"AP Halfwidth (ms): {halfwidth}")
    df["AP Halfwidth 5ms (ms)"] = halfwidth

    print(f"AP Falling Time Raw (ms): {fall_time_raw}")
    df["AP Falling Time Raw 5ms (ms)"] = fall_time_raw

    print(f"AP Falling Time 10-90 (ms): {fall_time_10_90}")
    df["AP Falling Time 10-90 5ms (ms)"] = fall_time_10_90

    print(f"AHP Minimum (mV): {ahp}")
    df["AHP Minimum 5ms (mV)"] = ahp

    print(f"AHP Relative (mV): {ahp - threshold_volt}")
    df["AHP Relative 5ms (mV)"] = ahp - threshold_volt

    print(f"AHP half-width (ms): {ahp_halfwidth}")
    df["AHP half-width 5ms (ms)"] = ahp_halfwidth

    print(f"Upstroke-Downstroke ratio: {rise_time_10_90 / fall_time_10_90}")
    df["Upstroke-Downstroke ratio 5ms"] = rise_time_10_90 / fall_time_10_90

    image_name = no_spaces(df.index[0]) + "_rheo_5ms_graph.png"
    save_plot(
        x=sweep_x,
        y= sweep_y,
        xlabel= x_label,
        ylabel= y_label,
        title= os.path.basename(image_name)[:-4],
        filename=image_name,
        folder=output_dir
    )

    phase_plane_table = phase_plane(sweep_x, sweep_y, sweep_y_d, df, step="5ms", output_dir=output_dir)

    return df, phase_plane_table