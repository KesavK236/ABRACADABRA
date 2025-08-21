import os
from logic.helpers import load_abf, num_sweeps, current_injection_start, ap_curr_and_time, adjust_units, no_spaces, save_plot, generate_derivatives, is_ramp
import numpy as np
from scipy.signal import savgol_filter

def rheo_1s(file_name, f, dvdt):

    if is_ramp(file_name):
        raise Exception("Rheo_1s file is not a Rheostep")
    print("Rheo_1s Data:")
    f.write("Rheo_1s Data:\n")

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
        _, sweep_x, sweep_y, sweep_y_raw, sweep_c, x_label, y_label, c_label, loaded, sample_rate = load_abf(file_name, sweep_num=i, smooth=True, loaded=loaded)

        sweep_y_d, sweep_x_d, _, _ = generate_derivatives(sweep_x, sweep_y)
        curr_start_index = current_injection_start(sweep_c)
        curr_end_index = curr_start_index + 1

        while curr_end_index < len(sweep_c) and sweep_c[curr_end_index] != 0:
            curr_end_index += 1
        curr_end_index -= 1

        if sweep_c[curr_start_index + 1] < 0:
            v_min = np.min(sweep_y)

            base_volt = np.mean(sweep_y[200:400])
            end_volt = np.mean(sweep_y[curr_end_index - 200:curr_end_index])
            end_curr = np.mean(sweep_c[curr_end_index - 200:curr_end_index])

            if len(hyper_pol_input_res_array) < 1:
                delta_sag = v_min - end_volt
                sag_ratio = delta_sag / (v_min - base_volt)
            
            hyper_pol_input_res_array.append(((end_volt - base_volt) * 1e-3) / (end_curr * 1e-12))


        ap_max = np.max(sweep_y)
        if sweep_c[curr_start_index + 1] > 0 and ap_bool == 0 and ap_max > 0:
            ap_bool, current_threshold, rheobase, ap_delay = ap_curr_and_time(sweep_x, sweep_y, sweep_c, sweep_y_d, sweep_x_d, curr_start_index, dvdt)

        if ap_bool == 1 and image_made_bool == 0:
            image_name = no_spaces(f.name[:-4]) + "_rheo_1s_graph.png"
            save_plot(
                x=sweep_x,
                y=sweep_y,
                xlabel=x_label,
                ylabel=y_label,
                title=os.path.basename(image_name)[:-4],
                filename=image_name,
                folder=os.path.dirname(f.name)
            )
            image_made_bool = 1

    if len(hyper_pol_input_res_array) > 0:
        omega = chr(0x3a9)
        for i in range(hyper_pol_input_res_array):
            print(f"Input Resistance of Sweep {i} (M{omega}): {hyper_pol_input_res_array[i]}")
            f.write(f"Input Resistance of Sweep {i} (Mega Ohms):, {hyper_pol_input_res_array[i]}\n")
        average_input_res = np.mean(hyper_pol_input_res_array)
        print(f"Average Input Resistance (M{omega}): {average_input_res}")
        f.write(f"Average Input Resistance (Mega Ohms):, {average_input_res}\n")
        print(f"Sag Peak (mV): {v_min}")
        f.write(f"Sag Peak (mV):, {v_min}\n")
        print(f"Delta Sag (mV): {delta_sag}")
        f.write(f"Delta Sag (mV):, {delta_sag}\n")
        print(f"Sag Ratio: {sag_ratio}")
        f.write(f"Sag Ratio:, {sag_ratio}\n")

    if ap_bool == 1:
        print(f"Rheobase (nA): {rheobase}")
        f.write(f"Rheobase (nA):, {rheobase}\n")
        ap_delay = adjust_units(ap_delay)
        print(f"Time to Spike (ms): {ap_delay}")
        f.write(f"Time to Spike (ms):, {ap_delay}\n")
    
    