import os
from logic.helpers import load_abf, no_spaces, save_plot

def rmp(file_name, f):

    # Priming output
    print("Rmp Data:")
    f.write("Rmp Data:\n")


    num_sweeps, sweep_x, sweep_y, sweep_c, x_label, y_label, c_label, loaded, sample_rate = load_abf(file_name, sweep_num=0, smooth=False)

    resting_potential = sweep_y.mean()

    print(f"Resting Membrane Potential (mV): {resting_potential}")
    f.write(f"Resting Membrane Potential (mV):, {resting_potential}\n")

    image_name = no_spaces(f.name[:-4]) + '_rmp_graph.png'
    image_path = save_plot(
        x=sweep_x,
        y=sweep_y,
        xlabel=x_label,
        ylabel=y_label,
        title=os.path.basename(image_name)[:-4],
        filename=image_name,
        folder=os.path.dirname(f.name)
    )