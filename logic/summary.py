from logic.rmp import rmp
from logic.rheo_1s import rheo_1s
from logic.rheo_4x import rheo_4x
from logic.ramp_1s import ramp_1s
from logic.ramp_4x import ramp_4x
from logic.short_rheo_5ms import short_rheo_5ms
from logic.short_rheo_1s import short_rheo_1s
import os
import pandas as pd
import numpy as np
import re

def callback(
    file_paths,
    output_name,
    dvdt,
    verify_threshold=False,
    verify_ap_counts=False,
    open_excel=False,
    open_phase=False,
    status_label=None,
    error_labels=None,
    root=None,
    status_callback=None,
    error_callback=None,
    threshold_window_callback=None,
    ap_count_window_callback=None
):
    """Run the single-cell analysis pipeline for selected protocol files.

    Parameters
    ----------
    file_paths : list[str]
        Per-protocol input file paths in UI order.
    output_name : str
        Base output name used for output directory and CSV naming.
    dvdt : float
        dV/dt threshold used by AP-detection protocols.
    verify_threshold : bool, optional
        Whether threshold-verification dialogs should be enabled.
    verify_ap_counts : bool, optional
        Whether AP-count verification dialogs should be enabled.
    open_excel : bool, optional
        Whether to open the final CSV output in Excel.
    open_phase : bool, optional
        Whether to open generated phase-plane CSV outputs in Excel.
    status_label : tkinter.Label, optional
        Legacy status label target for direct UI updates.
    error_labels : list[tkinter.Label], optional
        Legacy per-protocol error labels for direct UI updates.
    root : tkinter.Tk, optional
        Legacy root used for ``update_idletasks`` when callbacks are not supplied.
    status_callback : callable, optional
        Callback ``(text, color)`` used for thread-safe status updates.
    error_callback : callable, optional
        Callback ``(index, text)`` used for thread-safe error updates.
    threshold_window_callback : callable, optional
        Main-thread bridge used to open threshold-verification dialogs.
    ap_count_window_callback : callable, optional
        Main-thread bridge used to open AP-count verification dialogs.

    Returns
    -------
    str
        Path to the generated analyzed CSV file.
    """
    if not output_name:
        raise ValueError("Output file name cannot be empty.")

    def set_status(text, color="blue"):
        """Dispatch a status update via callback or legacy widgets.

        Parameters
        ----------
        text : str
            Status message text.
        color : str, optional
            Tk-compatible text color.

        Returns
        -------
        None
        """
        if status_callback is not None:
            status_callback(text, color)
            return
        if status_label is not None:
            status_label.config(text=text, fg=color)
        if root is not None:
            root.update_idletasks()

    def set_error(index, text):
        """Dispatch a protocol error update via callback or legacy widgets.

        Parameters
        ----------
        index : int
            Protocol row index in the UI.
        text : str
            Error message text.

        Returns
        -------
        None
        """
        if error_callback is not None:
            error_callback(index, str(text))
            return
        if error_labels is not None:
            error_labels[index].config(text=str(text))
        if root is not None:
            root.update_idletasks()

    # Create output directory
    folder_name = output_name + "_outputs"
    output_dir = os.path.join(os.getcwd(), folder_name)
    os.makedirs(output_dir, exist_ok=True)


    
    # create output df
    output_df = pd.DataFrame(index=[output_name])
    output_df.index.name = "Cell Name"

    error_msg = ""
    output_path = os.path.join(output_dir, output_name + "_analyzed.csv")
    no_file = "No File Chosen"
    if file_paths[0] != no_file:
        try:
            set_status("Running RMP Protocol...", "blue")
            output_df, error_msg = rmp(file_paths[0], output_df, output_dir)
            if error_msg != "":
                set_error(0, error_msg)
        except Exception as e:
            set_error(0, e)
    if file_paths[1] != no_file:
        try:
            set_status("Running Rheo 1s Protocol...", "blue")
            output_df, pp_1s, error_msg = short_rheo_1s(
                file_paths[1],
                output_df,
                dvdt,
                verify_threshold,
                output_dir,
                threshold_window_callback=threshold_window_callback
            )
            if error_msg != "":
                set_error(1, error_msg)
        except Exception as e:
            set_error(1, e)
    if file_paths[2] != no_file:
        try:
            set_status("Running Rheo 4x Protocol...", "blue")
            output_df, error_msg = rheo_4x(
                file_paths[2],
                output_df,
                dvdt,
                verify_ap_counts,
                output_dir,
                ap_count_window_callback=ap_count_window_callback
            )
            if error_msg != "":
                set_error(2, error_msg)
        except Exception as e:
            set_error(2, e)
    if file_paths[3] != no_file:
        try:
            set_status("Running Ramp 1s Protocol...", "blue")
            output_df, error_msg = ramp_1s(
                file_paths[3],
                output_df,
                dvdt,
                verify_threshold,
                output_dir,
                threshold_window_callback=threshold_window_callback
            )
            if error_msg != "":
                set_error(3, error_msg)
        except Exception as e:
            set_error(3, e)
    if file_paths[4] != no_file:
        try:
            set_status("Running Ramp 4x Protocol...", "blue")
            output_df, error_msg = ramp_4x(
                file_paths[4],
                output_df,
                dvdt,
                verify_ap_counts,
                output_dir,
                ap_count_window_callback=ap_count_window_callback
            )
            if error_msg != "":
                set_error(4, error_msg)
        except Exception as e:
            set_error(4, e)
    if file_paths[5] != no_file:
        try:
            set_status("Running Single AP 5ms...", "blue")
            output_df, pp_5ms, error_msg = short_rheo_5ms(
                file_paths[5],
                output_df,
                dvdt,
                verify_threshold,
                output_dir,
                threshold_window_callback=threshold_window_callback
            )
            if error_msg != "":
                set_error(5, error_msg)
        except Exception as e:
            set_error(5, e)

    version = 1.1

    print(f"ABRACADABRA Version: {version}")
    output_df["ABRACADABRA Version"] = version
    
    print(output_df)
    transposed_df = output_df.transpose()
    output_bool = True
    transposed_df.to_csv(output_path)
    while output_bool:
        try:
            
            output_bool = False
        except:
            number = re.search(r"\(\d+\)$", output_path)
            if number:
                file_number = int(number.group(1))
                new_num = f"({file_number + 1})"
                output_path = re.sub(r"\(\d+\)$", new_num, output_path)
            else:
                output_path = output_path + "(1)"


    if open_excel:
        os.system("start EXCEL.EXE " + output_path)

    if open_phase:
        if file_paths[5] != no_file:
            os.system("start EXCEL.EXE " + pp_5ms)
        if file_paths[1] != no_file:
            os.system("start EXCEL.EXE " + pp_1s)
    
    if error_msg == "":
        set_status("Analysis complete.", "green")
    else:
        set_status(error_msg, "red")

    return output_path
