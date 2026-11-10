import os

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


class NeedsReview(Exception):
    """Raised by a protocol when it flags data that needs the user to look at it,
    but it is running somewhere that cannot open a window (e.g. a multiprocessing worker).
    The batch runner catches this and re-runs the file on the GUI side so it can prompt."""


def adjust_units(num, figs=3):
    """Multipies the number by 1000 and rounds to the given number of significant figures.
    Parameters
    ----------
    num : float
        The number to be adjusted.
    figs : int, optional
        The number of significant figures to round to. Default is 3.
    Returns
    -------
    float
        The adjusted number.
    """
    num = num * 1000
    return round(num, figs)


def no_spaces(name):
    """Replaces spaces in the given filenames with underscores.
    Parameters
    ----------
    name : str
        The filename to be adjusted.
    Returns
    -------
    str
        The adjusted filename with spaces replaced by underscores.
    """
    return name.replace(" ", "_")


def check_no_change(sweep_y_d, j, increasing):
    """Checks if there is no change in the derivative for 10 consecutive points to confirm that the threshold has been crossed and it's not just noise.
    Parameters
    ----------
    sweep_y_d : 1D numpy array
        The first derivative of the voltage sweep.
    j : int
        The current index being checked.
    increasing : bool
        Whether the derivative is expected to be increasing or decreasing after crossing the threshold.
    Returns
    -------
    int
        1 if there is no change in the derivative for 10 consecutive points, 0 otherwise.
    """
    for i in range(10):
        if j + i >= len(sweep_y_d):
            break
        if sweep_y_d[j + i] > 0 and increasing:
            return 0
        if sweep_y_d[j + i] < 0 and not increasing:
            return 0
    return 1


def save_plot(x, y, xlabel, ylabel, title, filename, folder=None, markers=None, preview_png=False):
    """Generate and save a plot of the given x and y data.
    Parameters
    ----------
    x : array-like
        The x-axis data points.
    y : array-like
        The y-axis data points.
    xlabel : str
        The label for the x-axis.
    ylabel : str
        The label for the y-axis.
    title : str
        The title of the plot.
    filename : str
        The name of the file to save the plot as (including extension, e.g., "plot.png").
    folder : str, optional
        The folder to save the plot in. If None (default), the plot will be saved in the current directory.
    markers : list of tuples, optional
        A list of (x, y) tuples to mark on the plot. Default is None, meaning no markers will be added.
    preview_png : bool, optional
        If True, also save a PNG copy (PIL/Tk cannot display SVG) for the AP verification window.
        The caller is responsible for deleting it afterwards. Default is False.
    Returns
    -------
    str
        The path to the PNG preview if preview_png is True, otherwise the path to the saved SVG.
    """
    fig = Figure(figsize=(6, 4), dpi=200)
    ax = fig.add_subplot(111)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.plot(x, y, alpha=0.5)

    if markers:
        for (mx, my) in markers:
            ax.plot(mx, my, marker="o", markersize=3, color="green")

    if folder:
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)
    else:
        path = filename
    fig.suptitle(title.split("/")[-1])
    FigureCanvas(fig)
    base = os.path.splitext(path)[0]
    svg_path = base + ".svg"
    fig.savefig(svg_path, format="svg")
    out_path = svg_path
    if preview_png:
        out_path = base + ".png"
        fig.savefig(out_path, format="png")
    fig.clear()
    return out_path


def phase_plane(x, y, yd, df, step, output_dir):
    """Generates a phase plane plot of the voltage sweep and its derivative, saves the plot and a corresponding CSV file of the data.
    Parameters
    x : 1D numpy array
        The time points of the sweep in seconds.
    y : 1D numpy array
        The voltage values of the sweep in mV.
    yd : 1D numpy array
        The first derivative of the voltage sweep in mV/ms.
    df : DataFrame
        The DataFrame containing the sweep data, used to generate the filename and title for the plot.
    step : str
        The time step of the sweep ("5ms" or "1s"), used to generate the filename and title for the plot.
    output_dir : str
        The directory to save the plot and CSV file in.
    Returns
    -------
    str
        The path to the saved CSV file containing the phase plane data.
    """

    dfname = df.index[0]
    if step == "5ms":
        file_name = dfname + "_5ms_phase_plane"
        title = dfname + "5ms Phase Plane Plot"

    if step == "1s":
        file_name = dfname + "_1s_phase_plane"
        title = dfname + "1s Phase Plane Plot"

    table_file = os.path.join(output_dir, file_name + ".csv")

    with open(table_file, "w") as g:
        g.write("Time (s), Voltage (mV), dV/dt (mv/ms) \n")
        for i in range(len(yd)):
            g.write(f"{x[i]}, {y[i]}, {yd[i]} \n")

    save_plot(
        y[:-1],
        yd,
        "Volage (mV)",
        "dV/dt (mV/ms)",
        title,
        file_name + ".png",
        folder=os.path.dirname(table_file),
    )

    return table_file
