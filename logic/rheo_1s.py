import os
from logic.helpers import load_abf, num_sweeps, current_injection_points_rheo, ap_curr_and_time, adjust_units, no_spaces, save_plot, generate_derivatives, is_ramp
import numpy as np
from scipy.signal import savgol_filter

def rheo_1s(file_name, df, dvdt=20, output_dir=os.getcwd()):

    # if is_ramp(file_name):
    #     raise Exception("Rheo_1s file is not a Rheostep")
    print("Rheo_1s Data:")
    # f.write("Rheo_1s Data:\n")

    num_sweep = load_abf(file_name)[0]
    delta_sag = 0
    sag_ratio = 0
    ap_bool = 0
    current_threshold = 0
    rheobase = 0
    ap_delay = 0
    image_made_bool = 0
    loaded = None
    hyper_pol_input_res_array = []

    for i in range(num_sweep):
        _, sweep_x, sweep_y, sweep_y_raw, sweep_c, __, x_label, y_label, c_label, loaded, sample_rate = load_abf(file_name, sweep_num=i, smooth=True, loaded=loaded)

        if "(nA)" in c_label:
            current_units = "nA"
        elif "(pA)" in c_label:
            current_units = "pA"
        
        sweep_y_d, sweep_x_d, _, _ = generate_derivatives(sweep_x, sweep_y)
        curr_start_index, curr_end_index, holding_curr, stim_curr = current_injection_points_rheo(loaded, sample_rate, i, sweep_x, sweep_c)
        curr_diff = stim_curr - holding_curr
        if curr_diff < -1.5:
            v_min = np.min(sweep_y)

            base_volt = np.mean(sweep_y[200:400])
            end_volt = np.mean(sweep_y[curr_end_index - 200:curr_end_index])

            if len(hyper_pol_input_res_array) < 1:
                delta_sag = v_min - end_volt
                sag_ratio = delta_sag / (v_min - base_volt)
            if current_units == "nA":
                hyper_pol_input_res_array.append((((end_volt - base_volt) * 1e-3) / (curr_diff * 1e-9)) / 1e6)
            elif current_units == "pA":
                hyper_pol_input_res_array.append((((end_volt - base_volt) * 1e-3) / (curr_diff * 1e-12)) / 1e6)


        ap_max = np.max(sweep_y)
        if sweep_c[curr_start_index + 1] > 0 and ap_bool == 0 and ap_max > 0:
            ap_bool, current_threshold, rheobase, ap_delay = ap_curr_and_time(sweep_x, sweep_y, sweep_c, sweep_y_d, sweep_x_d, curr_start_index, curr_end_index, dvdt)
            stim_curr_rheobase = np.mean(sweep_c[curr_start_index+100:curr_end_index-100])
            holding_curr_rheobase = np.mean(sweep_c[curr_start_index-500:curr_start_index-10])
            rheobase = stim_curr_rheobase - holding_curr_rheobase

        if ap_bool == 1 and image_made_bool == 0:
            image_name = no_spaces(df.index[0]) + "_rheo_1s_graph.png"
            save_plot(
                x=sweep_x,
                y=sweep_y,
                xlabel=x_label,
                ylabel=y_label,
                title=os.path.basename(image_name)[:-4],
                filename=image_name,
                folder=output_dir
            )
            image_made_bool = 1

    if len(hyper_pol_input_res_array) > 0:
        omega = chr(0x3a9)
        for i in range(len(hyper_pol_input_res_array)):
            print(f"Input Resistance of Sweep {i} (M{omega}): {hyper_pol_input_res_array[i]}")
            df[f"Input Resistance of Sweep {i} (Mega Ohms)"] = hyper_pol_input_res_array[i]
        average_input_res = np.mean(hyper_pol_input_res_array)
        print(f"Average Input Resistance (M{omega}): {average_input_res}")
        df[f"Average Input Resistance (Mega Ohms)"] = average_input_res
        print(f"Sag Peak (mV): {v_min}")
        df["Sag Peak (mV)"] = v_min
        print(f"Delta Sag (mV): {delta_sag}")
        df[f"Delta Sag (mV)"] = delta_sag
        print(f"Sag Ratio: {sag_ratio}")
        df[f"Sag Ratio"] = sag_ratio

    if ap_bool == 1:
        print(f"Holding Current ({current_units}): {holding_curr_rheobase}")
        df[f"Holding Current Rheo ({current_units})"] = holding_curr_rheobase

        print(f"Rheobase ({current_units}): {stim_curr_rheobase}")
        df[f"Rheobase Rheo ({current_units})"] = stim_curr_rheobase
        print(f"Relative Rheobase ({current_units}): {rheobase}")
        df[f"Relative Rheobase Rheo ({current_units})"] = rheobase
        ap_delay = adjust_units(ap_delay)
        print(f"Time to Spike (ms): {ap_delay}")
        df[f"Time to Spike Rheo (ms)"] = ap_delay

    return df    
    