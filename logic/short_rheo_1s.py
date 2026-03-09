import os
from gui_check_threshold import check_thresh_window
from logic.processing import (
    ap_curr_and_time,
    current_injection_points_rheo,
    generate_derivatives,
    get_max,
    is_ramp,
    load_abf,
)
from logic.utils import adjust_units, no_spaces, phase_plane, save_plot
import numpy as np
from scipy.signal import find_peaks


def short_rheo_1s(file_name, df, dvdt=20, check_threshold=False, output_dir=os.getcwd(), threshold_window_callback=None):
    """Analyze the Short Rheo 1s protocol from an ABF file.

    Parameters
    ----------
    file_name : str
        Path to the ABF file containing Short Rheo 1s protocol data.
    df : pandas.DataFrame
        Output DataFrame to update with extracted metrics.
    dvdt : float, optional
        dV/dt threshold used for AP detection.
    check_threshold : bool, optional
        Whether to show threshold-verification UI.
    output_dir : str, optional
        Directory for generated plots and output files.
    threshold_window_callback : callable, optional
        Optional bridge for opening threshold-verification UI on the main thread.

    Returns
    -------
    tuple
        ``(df, phase_plane_table, error_msg)`` where ``df`` is the updated
        analysis DataFrame, ``phase_plane_table`` contains phase-plane output,
        and ``error_msg`` is an error string (empty when no error is reported).
    """
    num_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, __, x_label, y_label, c_label, loaded, sample_rate, current_units, current_record = load_abf(file_name)

    error_msg = ""

    if is_ramp(file_name):
            raise Exception("Rheo_1s file is not a Rheostep")

    print("Rheo_1s Data:")
    df["Rheo 1s"] = None
    # f.write(f"Rheo_1s Data:\n")

    curr_start_index, curr_end_index, holding_curr, stim_curr = current_injection_points_rheo(loaded, sample_rate, 0, sweep_x, sweep_c, current_units)

    curr_length = curr_end_index - curr_start_index
    standard_curr_start = curr_start_index

    
    sweep_index = 0
    threshold_checked = False
    passed_check_func = 0
    hyper_pol_input_res_array = []
    sag_peak = 0

    while sweep_index < num_sweeps and not threshold_checked:
        num_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, __,  x_label, y_label, c_label, loaded, sample_rate, current_units, current_record = load_abf(file_name, sweep_num=sweep_index, smooth=True, loaded=loaded, protocol="rheo", current_record=current_record)
        if not current_record:
            error_msg = "Current not recorded in Rheo 1s. Used Epoch instead."
        sweep_y_d, sweep_x_d, sweep_y_d2, sweep_x_d2 = generate_derivatives(sweep_x, sweep_y, hampel_bool=False)
        
        curr_start_index, curr_end_index, holding_curr, stim_curr = current_injection_points_rheo(loaded, sample_rate, sweep_index, sweep_x, sweep_c, current_units)

        curr_diff = stim_curr - holding_curr
        if curr_diff < -7.5:
            v_min = np.min(sweep_y)

            base_volt = np.mean(sweep_y[curr_start_index - 400: curr_start_index - 200])
            end_volt = np.mean(sweep_y[curr_end_index - 200:curr_end_index])
            if sweep_index == 0:
                sag_peak = v_min

            if len(hyper_pol_input_res_array) < 1:
                delta_sag = v_min - end_volt
                sag_ratio = delta_sag / (v_min - base_volt)
            hyper_pol_input_res_array.append((((end_volt - base_volt) * 1e-3) / (curr_diff * 1e-12)) / 1e6)
        
            
        sweep_y_post_curr = sweep_y_raw[curr_start_index:curr_end_index]
        sweep_y_d_post_curr = sweep_y_d[curr_start_index:curr_end_index]
        ap_max = max(sweep_y_post_curr)
        dvdt_max = max(sweep_y_d_post_curr)

        if ap_max >= 0 and dvdt_max >= 0:
            if passed_check_func == 0:
                upper_window = sweep_x[np.argmax(sweep_y_d)]
                lower_window = sweep_x[curr_start_index + int(0.0005 * sample_rate)]

            i = int(lower_window * sample_rate)
            
            sweep_y_d, sweep_x_d, sweep_y_d2, sweep_x_d2 = generate_derivatives(sweep_x, sweep_y, hampel_bool=True)


            while (sweep_y_d[i] < dvdt or sweep_y_d2[i] < 15) and sweep_x[i] < upper_window and i < curr_end_index:
                i += 1
            if i < curr_end_index - 100:
                threshold_index = i
                threshold_volt = sweep_y_raw[threshold_index]
                threshold_time = sweep_x[threshold_index] 
                threshold_curr = sweep_c[curr_start_index + 5]

                if threshold_window_callback is not None:
                    threshold_checked, upper_window, lower_window = threshold_window_callback(
                        check_thresh_window,
                        check_threshold,
                        upper_window,
                        lower_window,
                        sweep_x,
                        sweep_y,
                        threshold_index,
                        curr_start_index,
                        len(sweep_c) - 100
                    )
                else:
                    threshold_checked, upper_window, lower_window = check_thresh_window(
                        check_threshold,
                        upper_window,
                        lower_window,
                        sweep_x,
                        sweep_y,
                        threshold_index,
                        curr_start_index,
                        len(sweep_c) - 100
                    )
                passed_check_func = 1
            else:
                sweep_index += 1
        else:
            sweep_index += 1

        if threshold_checked == 2:
            sweep_index += 1
            threshold_checked = 0


    if threshold_checked == 1:
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
        rheobase = stim_curr - holding_curr
        curr_start_time = sweep_x[curr_start_index]
        relative_thresh_time = adjust_units((threshold_time-curr_start_time))
        relative_peak_time = adjust_units((peak_time-curr_start_time))

    # Store values and output
    if "(nA)" in c_label:
        current_units = "nA"
    elif "(pA)" in c_label:
        current_units = "pA"

    if len(hyper_pol_input_res_array) > 0:
        omega = chr(0x3a9)
        for i in range(len(hyper_pol_input_res_array)):
            print(f"Input Resistance of Sweep {i} (M{omega}): {hyper_pol_input_res_array[i]}")
            df[f"Input Resistance of Sweep {i} (Mega Ohms)"] = hyper_pol_input_res_array[i]
        average_input_res = np.mean(hyper_pol_input_res_array)
        print(f"Average Input Resistance (M{omega}): {average_input_res}")
        df[f"Average Input Resistance (Mega Ohms)"] = average_input_res
        print(f"Sag Peak (mV): {sag_peak}")
        df["Sag Peak (mV)"] = sag_peak
        print(f"Delta Sag (mV): {delta_sag}")
        df[f"Delta Sag (mV)"] = delta_sag
        print(f"Sag Ratio: {sag_ratio}")
        df[f"Sag Ratio"] = sag_ratio

    if threshold_checked == 1:
        print(f"Holding Current ({current_units}): {holding_curr}")
        df[f"Holding Current 1s ({current_units})"] = holding_curr

        print(f"Rheobase ({current_units}): {stim_curr}")
        df[f"Rheobase 1s ({current_units})"] = stim_curr

        print(f"Relative Rheobase ({current_units}): {rheobase}")
        df[f"Relative Rheobase 1s ({current_units})"] = rheobase
        print(f"Current start time: {curr_start_time}")

        print(f"AP Peak (mV): {filtered_peak_volt}")
        df["AP Peak 1s (mV)"] = filtered_peak_volt

        print(f"AP Amplitude (mV): {filtered_peak_volt - threshold_volt}")
        df["AP Amplitude 1s (mV)"] = filtered_peak_volt - threshold_volt

        print(f"Time of Peak (ms): {relative_peak_time}")
        print(f"Raw Peak Time: {peak_time}")
        df["Time of Peak 1s (ms)"] = relative_peak_time

        print(f"AP Voltage Threshold (mV): {threshold_volt}")
        df["AP Voltage Threshold 1s (mV)"] = threshold_volt

        print(f"Time of Threshold (ms): {relative_thresh_time}")
        print(f"Raw Thresh Time: {threshold_time}")
        df["Time of Threshold 1s (ms)"] =  relative_thresh_time

        print(f"AP Rise Time Raw (ms): {rise_time_raw}")
        df["AP Rise Time Raw 1s (ms)"] = rise_time_raw

        print(f"AP Rise Time 10-90 (ms): {rise_time_10_90}")
        df["AP Rise Time 10-90 1s (ms)"]  = rise_time_10_90

        print(f"AP Halfwidth (ms): {halfwidth}")
        df["AP Halfwidth 1s (ms)"] = halfwidth

        print(f"AP Falling Time Raw (ms): {fall_time_raw}")
        df["AP Falling Time Raw 1s (ms)"] = fall_time_raw

        print(f"AP Falling Time 10-90 (ms): {fall_time_10_90}")
        df["AP Falling Time 10-90 1s (ms)"] = fall_time_10_90

        print(f"AHP Minimum (mV): {ahp}")
        df["AHP Minimum 1s (mV)"] = ahp

        print(f"AHP Relative (mV): {ahp - threshold_volt}")
        df["AHP Relative 1s (mV)"] = ahp - threshold_volt

        print(f"AHP half-width (ms): {ahp_halfwidth}")
        df["AHP half-width 1s (ms)"] = ahp_halfwidth

        print(f"Upstroke-Downstroke ratio: {rise_time_10_90 / fall_time_10_90}")
        df["Upstroke-Downstroke ratio 1s"] = rise_time_10_90 / fall_time_10_90
    if threshold_checked == 0:
        print("No Action Potential Detected")
        error_msg = "No Action Potential Detected"
    image_name = no_spaces(df.index[0]) + "_rheo_1s_graph.png"
    save_plot(
        x=sweep_x,
        y= sweep_y,
        xlabel= x_label,
        ylabel= y_label,
        title= os.path.basename(image_name)[:-4],
        filename=image_name,
        folder=output_dir
    )

    phase_plane_table = phase_plane(sweep_x, sweep_y_raw, sweep_y_d, df, step="1s", output_dir=output_dir)

    return df, phase_plane_table, error_msg
