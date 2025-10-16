import os
import numpy as np
from logic.helpers import (
    load_abf, num_sweeps, current_injection_points_ramp, 
    ap_curr_and_time, adjust_units, no_spaces, save_plot, generate_derivatives, is_ramp
)

def ramp_1s(file_name, df, dvdt=20, verify_threshold=False, output_dir=os.getcwd()):

    print("Ramp_1s Data:")
    df["Ramp 1s"] = None
    # f.write("Ramp_1s Data:\n")
    error_msg = ""

    if not is_ramp(file_name):
        raise Exception("Ramp_1s file is not a Ramp")

    num_sweep = load_abf(file_name)[0]

    ap_bool = 0
    current_threshold = 0
    rheobase = 0
    ap_delay = 0
    image_made = False
    loaded = None
    current_record = -1

    i = 0
    while i < num_sweep and ap_bool == 0:
        _, sweep_x, sweep_y, sweep_y_raw, sweep_c, sweep_stim,  x_label, y_label, c_label, loaded, sample_rate, current_record = load_abf(file_name, sweep_num=i, smooth=True, loaded=loaded, protocol="ramp", current_record=current_record)
        if not current_record:
            error_msg = "Current not recorded in Ramp 1s. Used Epoch instead."
        sweep_y_d, sweep_x_d, _, _ = generate_derivatives(sweep_x, sweep_y)

        curr_start_index, curr_end_index, holding_curr, stim_curr = current_injection_points_ramp(loaded, sample_rate, i, sweep_x, sweep_c, sweep_stim)

        ap_max = max(sweep_y)
        if ap_bool == 0 and ap_max > 0:
            if "(nA)" in c_label:
                current_units = "nA"
            elif "(pA)" in c_label:
                current_units = "pA"
            ap_bool, current_threshold, rheobase, ap_delay = ap_curr_and_time(sweep_x, sweep_y, sweep_c, sweep_y_d, sweep_x_d, curr_start_index, curr_end_index, dvdt)
        
        if ap_bool == 1 and not image_made:
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
            image_made = True
        i += 1
    if i == num_sweep and ap_bool == 0:
        error_msg = "No Action Potential Detected in any sweep."
    if ap_bool:
        
        print(f"Holding Current ({current_units}): {holding_curr}")
        df[f"Holding Current Ramp 1s ({current_units})"] = holding_curr
        print(f"Rheobase ({current_units}): {rheobase}")
        df[f"Rheobase Ramp 1s ({current_units})"] = rheobase
        print(f"Relative Rheobase ({current_units}): {rheobase-holding_curr}")
        df[f"Relative Rheobase Ramp 1s ({current_units})"] = rheobase-holding_curr
        ap_delay = adjust_units(ap_delay)
        print(f"Time to Spike (ms): {ap_delay}")
        df["Time to Spike Ramp (ms)"] = ap_delay

    return df, error_msg