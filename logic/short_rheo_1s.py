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
from logic.utils import NeedsReview, adjust_units, check_no_change, no_spaces, phase_plane, save_plot
import numpy as np
from scipy.signal import find_peaks
import pandas as pd


def short_rheo_1s(file_name, df, isi_df, dvdt=20, check_threshold=False, get_rheo1s_freq=False, output_dir=os.getcwd(), threshold_window_callback=None, prompt_flagged=False, allow_prompt=True):
    """Analyze the Short Rheo 1s protocol from an ABF file.

    Parameters
    ----------
    file_name : str
        Path to the ABF file containing Short Rheo 1s protocol data.
    df : pandas.DataFrame
        Output DataFrame to update with extracted metrics.
    isi_df : pandas.DataFrame
        DataFrame to store inter-sweep interval data.
    dvdt : float, optional
        dV/dt threshold used for AP detection.
    check_threshold : bool, optional
        Whether to show threshold-verification UI.
    get_rheo1s_freq : bool, optional
        Whether to calculate and return the firing frequency of suprathreshold sweeps of the Rheo 1s protocol.
    output_dir : str, optional
        Directory for generated plots and output files.
    threshold_window_callback : callable, optional
        Optional bridge for opening threshold-verification UI on the main thread.
    prompt_flagged : bool, optional
        Whether a suspicious threshold (above the previous sweep's subthreshold peak) should
        open the check window when ``check_threshold`` is off. The check always runs; this only
        controls whether the user is prompted. Default is False.
    allow_prompt : bool, optional
        Whether a window may be opened for a flagged threshold. When False (e.g. in a multiprocessing worker),
        :class:`NeedsReview` is raised instead so the caller can re-run the file interactively.

    Returns
    -------
    tuple
        ``(df, isi_df, phase_plane_table, error_msg)`` where ``df`` is the updated
        analysis DataFrame, ``isi_df`` contains inter-sweep interval data, ``phase_plane_table`` contains phase-plane output,
        and ``error_msg`` is an error string (empty when no error is reported).
    """
    num_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, __, x_label, y_label, c_label, loaded, sample_rate, current_units, current_record = load_abf(file_name)

    error_msg = ""

    if is_ramp(file_name):
            raise Exception("Rheo_1s file is not a Rheostep")

    print("Rheo_1s Data:")
    df["Rheo 1s file name"] = file_name
    isi_df["File Name"] = file_name

    # f.write(f"Rheo_1s Data:\n")

    curr_start_index, curr_end_index, holding_curr, stim_curr = current_injection_points_rheo(loaded, sample_rate, 0, sweep_x, sweep_c, current_units)

    curr_length = curr_end_index - curr_start_index
    standard_curr_start = curr_start_index
    base_volt = np.mean(sweep_y[: curr_start_index - 200])

    
    sweep_index = 0
    threshold_checked = False
    passed_check_func = 0
    hyper_pol_input_res_array = []
    sag_peak = 0
    step = 1  # +1 walks forward through sweeps, -1 after "check previous sweep"
    sweep_peaks = {}  # sweep index -> max voltage during current injection
    hyperpol_done = set()  # sweeps already counted, so going back doesn't duplicate them

    while sweep_index < num_sweeps and not threshold_checked:
        num_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, __,  x_label, y_label, c_label, loaded, sample_rate, current_units, current_record = load_abf(file_name, sweep_num=sweep_index, smooth=True, loaded=loaded, protocol="rheo", current_record=current_record)
        if not current_record:
            error_msg = "Current not recorded in Rheo 1s. Used Epoch instead."
        sweep_y_d, sweep_x_d, sweep_y_d2, sweep_x_d2 = generate_derivatives(sweep_x, sweep_y, hampel_bool=False)
        
        curr_start_index, curr_end_index, holding_curr, stim_curr = current_injection_points_rheo(loaded, sample_rate, sweep_index, sweep_x, sweep_c, current_units)

        curr_diff = stim_curr - holding_curr
        if curr_diff < -7.5 and sweep_index not in hyperpol_done:
            hyperpol_done.add(sweep_index)
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
        sweep_peaks[sweep_index] = np.max(sweep_y_post_curr)
        sweep_y_d_post_curr = sweep_y_d[curr_start_index:curr_end_index]
        ap_max = max(sweep_y_post_curr)
        dvdt_max = max(sweep_y_d_post_curr)
        dvdt_min = min(sweep_y_d_post_curr)

        if ap_max >= 0 and dvdt_max >= 0:
            if passed_check_func == 0:
                upper_window = sweep_x[np.argmax(sweep_y_d)]
                lower_window = sweep_x[curr_start_index + int(0.0005 * sample_rate)]

            i = int(lower_window * sample_rate)
            
            sweep_y_d, sweep_x_d, sweep_y_d2, sweep_x_d2 = generate_derivatives(sweep_x, sweep_y, hampel_bool=True)


            # threshold is the first point of a run where dV/dt stays >= dvdt for 0.1 ms,
            # so noise on the passive charging ramp isn't mistaken for the AP upstroke
            sustain_points = max(1, int(0.0001 * sample_rate))
            while sweep_x[i] < upper_window and i < curr_end_index:
                if np.all(sweep_y_d[i:i + sustain_points] >= dvdt):
                    break
                i += 1
            if i < curr_end_index - 100:
                threshold_index = i
                threshold_volt = sweep_y_raw[threshold_index]
                threshold_time = sweep_x[threshold_index] 
                threshold_curr = sweep_c[curr_start_index + 5]
                # every earlier sweep was visited on the way here, so its peak is recorded
                last_sweep_peak_volt = sweep_peaks.get(sweep_index - 1, base_volt)
                voltage_diff = threshold_volt - last_sweep_peak_volt

                # Flag: threshold sits above the previous sweep's subthreshold peak.
                # Always checked; only prompts (forces the window for this sweep) when
                # prompt_flagged is on and the normal threshold check is off.
                flagged = voltage_diff < 0
                if flagged:
                    print(f"Flagged sweep {sweep_index}: threshold {threshold_volt} mV > previous peak {last_sweep_peak_volt} mV")
                flagged = flagged and prompt_flagged and not check_threshold
                if flagged and not allow_prompt:
                    raise NeedsReview(
                        f"Rheo 1s sweep {sweep_index}: threshold ({threshold_volt:.2f} mV) is above "
                        f"previous sweep peak ({last_sweep_peak_volt:.2f} mV)"
                    )
                show_window = check_threshold or flagged

                if threshold_window_callback is not None:
                    threshold_checked, upper_window, lower_window = threshold_window_callback(
                        check_thresh_window,
                        show_window,
                        upper_window,
                        lower_window,
                        sweep_x,
                        sweep_y,
                        threshold_index,
                        curr_start_index,
                        len(sweep_c) - 100,
                        file_name=file_name,
                        sweep_index=sweep_index
                    )
                else:
                    threshold_checked, upper_window, lower_window = check_thresh_window(
                        show_window,
                        upper_window,
                        lower_window,
                        sweep_x,
                        sweep_y,
                        threshold_index,
                        curr_start_index,
                        len(sweep_c) - 100,
                        file_name=file_name,
                        sweep_index=sweep_index
                    )
                passed_check_func = 1
            else:
                sweep_index += step
        else:
            sweep_index += step

        if threshold_checked == 2:
            step = 1
            sweep_index += step
            threshold_checked = 0
        elif threshold_checked == 3:
            step = -1
            sweep_index += step
            threshold_checked = 0

        if sweep_index < 0:
            # no earlier sweep with an AP; head forward again
            sweep_index = 0
            step = 1



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

        print(f"Max Rise dV/dt (mV/ms): {dvdt_max}")
        df["Max Rise dV/dt 1s (mV/ms)"] = dvdt_max

        print(f"AP Halfwidth (ms): {halfwidth}")
        df["AP Halfwidth 1s (ms)"] = halfwidth

        print(f"AP Falling Time Raw (ms): {fall_time_raw}")
        df["AP Falling Time Raw 1s (ms)"] = fall_time_raw

        print(f"AP Falling Time 10-90 (ms): {fall_time_10_90}")
        df["AP Falling Time 10-90 1s (ms)"] = fall_time_10_90
 
        print(f"Min Rise dV/dt (mV/ms): {dvdt_min}")
        df["Min Rise dV/dt 1s (mV/ms)"] = dvdt_min
        
        print(f"AHP Minimum (mV): {ahp}")
        df["AHP Minimum 1s (mV)"] = ahp

        print(f"AHP Relative (mV): {ahp - threshold_volt}")
        df["AHP Relative 1s (mV)"] = ahp - threshold_volt

        print(f"AHP half-width (ms): {ahp_halfwidth}")
        df["AHP half-width 1s (ms)"] = ahp_halfwidth

        print(f"Upstroke-Downstroke ratio: {rise_time_10_90 / fall_time_10_90}")
        df["Upstroke-Downstroke ratio 1s"] = rise_time_10_90 / fall_time_10_90

        # # for revision data
        # num_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, __,  x_label, y_label, c_label, loaded, sample_rate, current_units, current_record = load_abf(file_name, sweep_num=sweep_index - 1, smooth=True, loaded=loaded, protocol="rheo", current_record=current_record)
        # print(f"SubThreshold peak voltage (mV): {np.max(sweep_y_raw[curr_start_index:curr_end_index])}")
        # df["SubThreshold peak voltage (mV)"] = np.max(sweep_y_raw[curr_start_index:curr_end_index])


    if get_rheo1s_freq and threshold_checked == 1:
        print(f"Rheobase current ({current_units}): {rheobase}")
        isi_df[f"Rheobase current ({current_units})"] = rheobase
        print(f"Rheobase sweep index: {sweep_index}")
        isi_df[f"Rheobase sweep index"] = sweep_index
        rheo_sweep_index = sweep_index
        while sweep_index < num_sweeps:
            num_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, __,  x_label, y_label, c_label, loaded, sample_rate, current_units, current_record = load_abf(file_name, sweep_num=sweep_index, smooth=True, loaded=loaded, protocol="rheo", current_record=current_record)
            sweep_y_d, sweep_x_d, sweep_y_d2, sweep_x_d2 = generate_derivatives(sweep_x, sweep_y, hampel_bool=False)
            
            curr_start_index, curr_end_index, holding_curr, stim_curr = current_injection_points_rheo(loaded, sample_rate, sweep_index, sweep_x, sweep_c, current_units)

            j = curr_start_index - 100
            ap_found = 0
            finding_peak = 0
            ap_count = 0
            threshold_ram = 0
            points = []
            while j < len(sweep_y_d) - 1:
                if sweep_y_d[j] >= dvdt and ap_found == 0 and finding_peak == 0:
                    # plt1.plot(sweep_x[j], sweep_y[j], 'ro')  # Mark the detected AP with a red dot
                    # plt.plot(sweep_x_d[j], sweep_y_d[j], 'ro')
        
                    ap_found = 1
                    finding_peak = 1
                    threshold_ram = sweep_y[j]
    
                elif finding_peak == 1 and sweep_y_d[j] < 0 < sweep_y[j] and (sweep_y[j] - threshold_ram > dvdt):
                    if check_no_change(sweep_y_d, j, increasing=True):
                        # plt1.plot(sweep_x[j], sweep_y[j], 'go')  # Mark the detected peak with a green dot
                        # plt.plot(sweep_x_d[j], sweep_y_d[j], 'go')  # Mark the detected peak with a green dot
            
                        if ap_count == 0:
                            dvdt = 5
                        finding_peak = 0
                        ap_count += 1
                        points.append((sweep_x[j], sweep_y[j]))
                elif finding_peak == 0 and ap_found == 1 and sweep_y_d[j] > 0:
                    if check_no_change(sweep_y_d, j, increasing=False):
                        # plt1.plot(sweep_x_d[j], sweep_y_d[j], 'bo')  # Mark the end of the AP with a blue dot
                        # plt.plot(sweep_x_d[j], sweep_y_d[j], 'bo')
            
                        ap_found = 0
                j += 1
            rel_sweep_index = sweep_index - rheo_sweep_index
            if len(points) >= 1:
                isi = np.diff([p[0] for p in points])
                mean_isi = np.mean(isi)
                sd_isi = np.std(isi)
                cv_isi = sd_isi / mean_isi if mean_isi != 0 else float('nan')
                if rel_sweep_index == 0:
                    print(f"Number of APs at Rheobase: {ap_count}")
                    isi_df[f"Number of APs at Rheobase"] = ap_count
                    print(f"Mean ISI at Rheobase (ms): {mean_isi}")
                    isi_df[f"Mean ISI at Rheobase (ms)"] = mean_isi
                    print(f"CV ISI at Rheobase (ms): {cv_isi}")
                    isi_df[f"CV ISI at Rheobase (ms)"] = cv_isi
                else:
                    print(f"Stimulus Current {rel_sweep_index} sweep after Rheobase ({current_units}): {stim_curr}")
                    isi_df[f"Stimulus Current {rel_sweep_index} sweep after Rheobase ({current_units})"] = stim_curr
                    print(f"Number of APs {rel_sweep_index} sweep after Rheobase: {ap_count}")
                    isi_df[f"Number of APs {rel_sweep_index} sweep after Rheobase"] = ap_count
                    print(f"Mean ISI {rel_sweep_index} sweep after Rheobase (ms): {mean_isi}")
                    isi_df[f"Mean ISI {rel_sweep_index} sweep after Rheobase (ms)"] = mean_isi
                    print(f"CV ISI {rel_sweep_index} sweep after Rheobase (ms): {cv_isi}")
                    isi_df[f"CV ISI {rel_sweep_index} sweep after Rheobase (ms)"] = cv_isi
            elif rel_sweep_index > 0:
                if rel_sweep_index == 0:
                    print(f"Number of APs at Rheobase: {ap_count}")
                    isi_df[f"Number of APs at Rheobase"] = ap_count
                    print(f"Mean ISI at Rheobase (ms): N/A")
                    isi_df[f"Mean ISI at Rheobase (ms)"] = np.nan
                    print(f"CV ISI at Rheobase (ms): N/A")
                    isi_df[f"CV ISI at Rheobase (ms)"] = np.nan
                else:
                    print(f"Stimulus Current {rel_sweep_index} sweep after Rheobase ({current_units}): {stim_curr}")
                    isi_df[f"Stimulus Current {rel_sweep_index} sweep after Rheobase ({current_units})"] = stim_curr
                    print(f"Number of APs {rel_sweep_index} sweep after Rheobase: {ap_count}")
                    isi_df[f"Number of APs {rel_sweep_index} sweep after Rheobase"] = ap_count
                    print(f"Mean ISI {rel_sweep_index} sweep after Rheobase (ms): N/A")
                    isi_df[f"Mean ISI {rel_sweep_index} sweep after Rheobase (ms)"] = np.nan
                    print(f"CV ISI {rel_sweep_index} sweep after Rheobase (ms): N/A")
                    isi_df[f"CV ISI {rel_sweep_index} sweep after Rheobase (ms)"] = np.nan

            sweep_index += 1
        
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

    phase_plane_table = phase_plane(sweep_x, sweep_y_raw, sweep_y_d, sweep_c, current_units, df, step="1s", output_dir=output_dir)

    return df, isi_df, phase_plane_table, error_msg
