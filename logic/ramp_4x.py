import os
import numpy as np
from logic.processing import (
    ap_curr_and_time,
    current_injection_points_ramp,
    generate_derivatives,
    is_ramp,
    load_abf,
)
from logic.utils import adjust_units, no_spaces, save_plot

from gui_ap_verify import ap_count_window
import matplotlib.pyplot as plt

def ramp_4x(file_name, df, dvdt=20, check_ap_counts=False, output_dir=os.getcwd(), ap_count_window_callback=None):
    """Analyze Ramp 4x protocol data from an ABF file.

    Parameters
    ----------
    file_name : str
        Path to the ABF file containing Ramp 4x protocol data.
    df : pandas.DataFrame
        Output DataFrame to update with extracted metrics.
    dvdt : float, optional
        dV/dt threshold used during AP detection.
    check_ap_counts : bool, optional
        Whether to show AP-count verification UI.
    output_dir : str, optional
        Directory for generated plots and output files.
    ap_count_window_callback : callable, optional
        Optional bridge for opening AP-count verification UI on the main thread.

    Returns
    -------
    tuple
        ``(df, error_msg)`` where ``df`` is the updated DataFrame and
        ``error_msg`` is an error string (empty when no error is reported).
    """
    
    if not is_ramp(file_name):
        raise Exception("Ramp_4x file is not a Rheostep")

    print("Ramp_4x Data:")
    df["Ramp 4x"] = None
    # f.write("Ramp_4x Data:\n")

    error_msg = ""
    ap_counts = [0, 0, 0, 0]
    holding_currs = [0, 0, 0, 0]
    stim_currs = [0, 0, 0, 0]
    image_names = ["", "", "", ""]
    loaded = None
    current_record = -1
    num_sweeps = load_abf(file_name)[0]

    for i in range(num_sweeps):
        _, sweep_x, sweep_y, sweep_y_raw, sweep_c, sweep_stim,  x_label, y_label, c_label, loaded, sample_rate, current_units, current_record = load_abf(file_name, sweep_num=i, smooth=True, loaded=loaded, protocol="ramp", current_record=current_record)
        if not current_record:
            error_msg = "Current not recorded in Ramp 4x. Used Epoch instead."
        sweep_y_d, sweep_x_d, *_ = generate_derivatives(sweep_x, sweep_y)

        units = loaded.sweepUnitsC
        if "nA" in units:
                current_units = "nA"
        elif "pA" in units:
                current_units = "pA"
        curr_start_index, curr_end_index, holding_curr, stim_curr = current_injection_points_ramp(loaded, sample_rate, i, sweep_x, sweep_c, sweep_stim, current_units)

        j = curr_start_index + 30
        ap_found = 0
        finding_peak = 0
        ap_count = 0
        threshold_ram = 0

        dvdt = 10
        points = []

        while j < len(sweep_y_d) - 1 and j < curr_end_index - 20:
            if sweep_y_d[j] >= dvdt and ap_found == 0 and finding_peak == 0:
                # plt1.plot(sweep_x[j], sweep_y[j], 'ro')  # Mark the detected AP with a red dot
                # plt2.plot(sweep_x_d[j], sweep_y_d[j], 'ro')
                ap_found = 1
                finding_peak = 1
                threshold_ram = sweep_y[j]

            elif finding_peak == 1 and sweep_y_d[j] < 0 < sweep_y[j] and (sweep_y[j] - threshold_ram > dvdt):

                if all(sweep_y_d[j + k] < 0 for k in range(10) if j + k < len(sweep_y_d)):
                    finding_peak = 0
                    # plt1.plot(sweep_x[j], sweep_y[j], 'go')  # Mark the detected peak with a green dot
                    # plt2.plot(sweep_x_d[j], sweep_y_d[j], 'go')  # Mark the detected peak with a green dot
                    if ap_count == 0:
                        dvdt = 4
                    ap_count += 1
                    points.append((sweep_x[j], sweep_y[j]))

            elif finding_peak == 0 and ap_found == 1 and sweep_y_d[j] > 0:
                if all(sweep_y_d[j + k] > 0 for k in range(10) if j + k < len(sweep_y_d)):
                    # plt1.plot(sweep_x[j], sweep_y[j], 'bo')  # Mark the end of the AP with a blue dot
                    # plt2.plot(sweep_x_d[j], sweep_y_d[j], 'bo')
                    ap_found = 0

            j += 1
        
        image_name = no_spaces(df.index[0]) + f"_ramp_{i+1}x_graph.png"
        image_names[i] = save_plot(
            x=sweep_x,
            y=sweep_y,
            xlabel=x_label,
            ylabel=y_label,
            title=os.path.basename(image_name)[:-4],
            filename=image_name,
            folder= output_dir,
            markers=points,
            preview_png=check_ap_counts
        )
        # fig, axs = plt.subplots(2, 1)
        # plt1 = axs[0]
        # plt2 = axs[1]
        # plt1.plot(sweep_x, sweep_y)
        # plt2.plot(sweep_x_d, sweep_y_d)

        ap_counts[i] = ap_count
        holding_currs[i] = holding_curr
        stim_currs[i] = stim_curr  

    if check_ap_counts:
        try:
            if ap_count_window_callback is not None:
                ap_counts[:] = ap_count_window_callback(ap_count_window, image_names, ap_counts)
            else:
                ap_counts[:] = ap_count_window(image_names, ap_counts)
        finally:
            # PNGs are only temporary previews for the verification window
            for png in image_names:
                if png and png.endswith(".png") and os.path.exists(png):
                    try:
                        os.remove(png)
                    except OSError as e:
                        print(f"Could not delete preview {png}: {e}")

    for i in range(num_sweeps):
        print(f"Holding Current at Ramp {i+1}x rheobase: {holding_currs[i]}")
        df[f"Holding Current at Ramp {i+1}x rheobase"] = holding_currs[i]
        print(f"Stimulus Current at Ramp {i+1}x rheobase: {stim_currs[i]}")
        df[f"Stimulus Current at Ramp {i+1}x rheobase"] = stim_currs[i]
        print(f"Relative Current Step at Ramp {i+1}x rheobase: {stim_currs[i]-holding_currs[i]}")
        df[f"Relative Current Step at Ramp {i+1}x rheobase"] = stim_currs[i]-holding_currs[i]
        print(f"Number of Action Potentials in Ramp {i+1}x: {ap_counts[i]}")
        df[f"Number of Action Potentials in Ramp {i+1}x"] = ap_counts[i]
    
    return df, error_msg
