import os
from logic.helpers import load_abf, no_spaces, save_plot
import pandas as pd

def rmp(file_name, df, output_dir=os.getcwd()):

    # Priming output
    print("Rmp Data:")
    df["RMP"] = None
    # f.write("Rmp Data:\n")
    error_msg = ""
    num_sweeps, sweep_x, sweep_y, sweep_y_raw, sweep_c, __,  x_label, y_label, c_label, loaded, sample_rate, current_record = load_abf(file_name, sweep_num=0, smooth=False)

    resting_potential = sweep_y.mean()

    print(f"Resting Membrane Potential (mV): {resting_potential}")
    df["Resting Membrane Potential (mV)"] = resting_potential

    image_name = no_spaces(df.index[0]) + '_rmp_graph.png'
    image_path = save_plot(
        x=sweep_x,
        y=sweep_y,
        xlabel=x_label,
        ylabel=y_label,
        title=os.path.basename(image_name)[:-4],
        filename=image_name,
        folder=output_dir
    )

    print(df)
    return df, error_msg