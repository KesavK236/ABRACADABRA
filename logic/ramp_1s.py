import os
import numpy as np
from logic.helpers import (
    load_abf, num_sweeps, current_injection_start, 
    ap_curr_and_time, two_sig_figs, no_spaces, save_plot, generate_derivatives
)

def ramp_1s(file_name, f, dvdt, verify_threshold):

    print("Ramp_1s Data:")
    f.write("Ramp_1s Data:\n")

    num_sweep = load_abf(file_name)[0]

    ap_bool = 0
    current_threshold = 0
    rheobase = 0
    ap_delay = 0
    image_made = False
    loaded = None

    for i in range(num_sweep):
        _, sweep_x, sweep_y, sweep_c, x_label, y_label, c_label, loaded, sample_rate = load_abf(file_name, sweep_num=i, smooth=True, loaded=loaded)
        sweep_y_d, sweep_x_d, _, _ = generate_derivatives(sweep_x, sweep_y)

        curr_start_index = current_injection_start(sweep_c)

        ap_max = max(sweep_y)
        if sweep_c[curr_start_index + 100] > 0 and ap_bool == 0 and ap_max > 0:
            ap_bool, current_threshold, rheobase, ap_delay = ap_curr_and_time(sweep_x, sweep_y, sweep_c, sweep_y_d, sweep_x_d, curr_start_index, dvdt)
        
        if ap_bool == 1 and not image_made:
            image_name = no_spaces(f.name[:-4]) + f"_ramp_1s_graph.png"
            save_plot(
                x=sweep_x,
                y=sweep_y,
                xlabel=x_label,
                ylabel=y_label,
                title=os.path.basename(image_name)[:-4],
                filename=image_name,
                folder=os.path.dirname(f.name)
            )
            image_made = True

    if ap_bool:
    
        print(f"Rheobase (nA): {rheobase}")
        f.write(f"Rheobase (nA):, {rheobase}\n")
        ap_delay = two_sig_figs(ap_delay)
        print(f"Time to Spike (ms): {ap_delay}")
        f.write(f"Time to Spike (ms):, {ap_delay}\n")