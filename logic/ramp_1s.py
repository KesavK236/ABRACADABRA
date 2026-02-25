import os
import numpy as np
from gui_check_threshold import check_thresh_window
from logic.helpers import (
    load_abf, num_sweeps, current_injection_points_ramp, 
    ap_curr_and_time, adjust_units, no_spaces, save_plot, generate_derivatives, is_ramp
)

def ramp_1s(file_name, df, dvdt=20, check_threshold=False, output_dir=os.getcwd()):

    print("Ramp_1s Data:")
    df["Ramp 1s"] = None
    # f.write("Ramp_1s Data:\n")
    error_msg = ""

    if not is_ramp(file_name):
        raise Exception("Ramp_1s file is not a Ramp")

    num_sweep = load_abf(file_name)[0]


    threshold_time = 0
    image_made = False
    loaded = None
    current_record = -1
    passed_check_func = 0
    threshold_checked = 0

    index_in_sweep = 0
    sweep_index = 0
    while sweep_index < num_sweep and threshold_checked == 0:
        _, sweep_x, sweep_y, sweep_y_raw, sweep_c, sweep_stim,  x_label, y_label, c_label, loaded, sample_rate, current_units, current_record = load_abf(file_name, sweep_num=sweep_index, smooth=True, loaded=loaded, protocol="ramp", current_record=current_record)
        if not current_record:
            error_msg = "Current not recorded in Ramp 1s. Used Epoch instead."
        sweep_y_d, sweep_x_d, _, _ = generate_derivatives(sweep_x, sweep_y)
        dvdt_max = max(sweep_y_d)

        units = loaded.sweepUnitsC
        if "nA" in units:
                current_units = "nA"
        elif "pA" in units:
                current_units = "pA"
        
        curr_start_index, curr_end_index, holding_curr, stim_curr = current_injection_points_ramp(loaded, sample_rate, sweep_index, sweep_x, sweep_c, sweep_stim, current_units)

        ap_max = max(sweep_y)
        if ap_max > 0 and dvdt_max >= dvdt:
            
            
            if passed_check_func == 0:
                upper_window = sweep_x[np.argmax(sweep_y_d)]
                lower_window = sweep_x[curr_start_index + int(0.0005 * sample_rate)]

            index_in_sweep = int(lower_window * sample_rate)
            
            sweep_y_d, sweep_x_d, sweep_y_d2, sweep_x_d2 = generate_derivatives(sweep_x, sweep_y, hampel_bool=True)


            while (sweep_y_d[index_in_sweep] < dvdt) and sweep_x[index_in_sweep] < upper_window and index_in_sweep < curr_end_index:
                index_in_sweep += 1
            if index_in_sweep < curr_end_index - 100:
                threshold_index = index_in_sweep
                threshold_volt = sweep_y_raw[threshold_index]
                threshold_time = sweep_x[threshold_index-curr_start_index] 
                threshold_curr = sweep_c[threshold_index]

                threshold_checked, upper_window, lower_window = check_thresh_window(check_threshold, upper_window, lower_window, sweep_x, sweep_y, threshold_index, curr_start_index, len(sweep_c) - 100)
                passed_check_func = 1

                if threshold_checked == 0:
                    sweep_index -=1

        if threshold_checked == 2:
            threshold_checked = 0

        
        
        if threshold_checked == 0:
            sweep_index += 1
    if sweep_index == num_sweep and threshold_checked == 0:
        error_msg = "No Action Potential Detected in any sweep."
    
    
    if threshold_checked == 1:
        
        image_name = no_spaces(df.index[0]) + f"_ramp_1s_graph.png"
        save_plot(
            x=sweep_x,
            y=sweep_y,
            xlabel=x_label,
            ylabel=y_label,
            title=os.path.basename(image_name)[:-4],
            filename=image_name,
            folder=output_dir
        )
        
        print(f"Holding Current ({current_units}): {holding_curr}")
        df[f"Holding Current Ramp 1s ({current_units})"] = holding_curr
        print(f"Rheobase ({current_units}): {stim_curr}")
        df[f"Rheobase Ramp 1s ({current_units})"] = stim_curr
        print(f"Relative Rheobase ({current_units}): {stim_curr-holding_curr}")
        df[f"Relative Rheobase Ramp 1s ({current_units})"] = stim_curr-holding_curr
        threshold_time = adjust_units(threshold_time)
        print(f"Time to Spike (ms): {threshold_time}")
        df["Time to Spike Ramp (ms)"] = threshold_time
        print(f"Voltage at Threshold Ramp 1s (mV): {threshold_volt}")
        df["Voltage at Threshold Ramp 1s (mV)"] = threshold_volt
        print(f"Current at Threshold Ramp 1s (pA): {threshold_curr}")
        df["Current at Threshold Ramp 1s (pA)"] = threshold_curr
    return df, error_msg