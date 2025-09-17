import os
import numpy as np
from logic.helpers import (
    load_abf, current_injection_points_rheo, num_sweeps,
    generate_derivatives, check_no_change, no_spaces,
    save_plot, is_ramp
)

from gui_ap_verify import ap_count_window

def rheo_4x(file_name, df, dvdt=20, check_ap_counts=False, output_dir=os.getcwd()):
    # if is_ramp(file_name):
    #     raise Exception("Rheo_4x file is not a Rheostep")

    print("Rheo_4x Data:")
    # f.write("Rheo_4x Data:\n")

    num_sweeps = load_abf(file_name)[0]
    ap_counts = [0, 0, 0, 0]
    image_names = ["", "", "", ""]
    loaded = None

    for i in range(4):
        _, sweep_x, sweep_y, sweep_y_raw, sweep_c, __,  x_label, y_label, c_label, loaded, sample_rate = load_abf(file_name, sweep_num=i, smooth=True, loaded=loaded)
        sweep_y_d, sweep_x_d, *_ = generate_derivatives(sweep_x, sweep_y)
        curr_start_index, curr_end_index, holding_curr, stim_curr = current_injection_points_rheo(loaded, sample_rate, i, sweep_x, sweep_c)

        j = curr_start_index + 30
        ap_found = 0
        finding_peak = 0
        ap_count = 0
        threshold_ram = 0

        image_name = no_spaces(df.index[0]) + f"_rheo_{i+1}x_graph.png"
        save_plot(
            x=sweep_x,
            y=sweep_y,
            xlabel=x_label,
            ylabel=y_label,
            title=os.path.basename(image_name)[:-4],
            filename=image_name,
            folder=output_dir
        )
        image_names[i] = os.path.join(output_dir, image_name)

        while j < len(sweep_y_d) - 1:
            if sweep_y_d[j] >= dvdt and ap_found == 0 and finding_peak == 0:
                ap_found = 1
                finding_peak = 1
                threshold_ram = sweep_y[j]

            elif finding_peak == 1 and sweep_y_d[j] < 0 < sweep_y[j] and (sweep_y[j] - threshold_ram > dvdt):
                if check_no_change(sweep_y_d, j, increasing=True):
                    finding_peak = 0
                    ap_count += 1

            elif finding_peak == 0 and ap_found == 1 and sweep_y_d[j] > 0:
                if check_no_change(sweep_y_d, j, increasing=False):
                    ap_found = 0

            j += 1

        ap_counts[i] = ap_count

    if check_ap_counts:
        ap_counts[:] = ap_count_window(image_names, ap_counts)

    for i in range(4):
        print(f"Number of Action Potentials in Rheo {i+1}x rheobase: {ap_counts[i]}")
        df[f"Number of Action Potentials in Rheo {i+1}x rheobase"] = ap_counts[i]

    return df