import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
from logic.rmp import rmp
from logic.rheo_4x import rheo_4x
from logic.ramp_1s import ramp_1s
from logic.ramp_4x import ramp_4x
from logic.short_rheo_5ms import short_rheo_5ms
from logic.short_rheo_1s import short_rheo_1s
import datetime



def list_abf_files(folder: str) -> list[str]:
    """List all ABF files in a given folder and its subfolders.
    
    Parameters
    ---------- 
    folder : str
        Path to the folder to search for ABF files.
    
    Returns
    -------
    list[str]
        List of full file paths to ABF files found in the folder."""
    out = []
    for dirpath, _, filenames in os.walk(folder):
        for f in filenames:
            if f.lower().endswith(".abf"):
                out.append(os.path.join(dirpath, f))
    return out

def run_task(task: dict, output_base_dir: str) -> pd.DataFrame:
    """Run a single analysis task based on the provided protocol and file path.

    Parameters
    ----------
    task : dict
        A dictionary containing the file path and analysis type.
    output_base_dir : str
        The base directory to save the analysis results.
    
    Returns
    -------
    pd.DataFrame
        A DataFrame containing the analysis results.
    """
    file_path = task["file_path"]
    analysis_type = task["protocol"]
    df = pd.DataFrame(index=[os.path.basename(file_path)])
    dvdt = task["dvdt"]
    safe_stem = os.path.splitext(os.path.basename(file_path))[0]
    output_dir = os.path.join(output_base_dir, analysis_type, safe_stem)
    os.makedirs(output_dir, exist_ok=True)
    if analysis_type == "RMP":
        try:
            result_df, error_msg = rmp(file_path, df, output_dir)
            if error_msg != "":
                result_df["Errors in RMP"] = error_msg
            df = result_df
        except Exception as e:
            error_msg = str(e)
            df["Errors in RMP"] = error_msg
    elif analysis_type == "Rheo 1s":
        try:
            result_df, pp1s, error_msg = short_rheo_1s(file_path, df, dvdt, check_threshold=False, output_dir=output_dir)
            if error_msg != "":
                result_df["Errors in Rheo 1s"] = error_msg
            df = result_df
        except Exception as e:
            error_msg = str(e)
            df["Errors in Rheo 1s"] = error_msg
    elif analysis_type == "Rheo 4x":
        try:
            result_df, error_msg = rheo_4x(file_path, df, dvdt, check_ap_counts=False, output_dir=output_dir)
            if error_msg != "":
                result_df["Errors in Rheo 4x"] = error_msg
            df = result_df
        except Exception as e:
            error_msg = str(e)
            df["Errors in Rheo 4x"] = error_msg
    elif analysis_type == "Ramp 1s":
        try:
            result_df, error_msg = ramp_1s(file_path, df, dvdt, check_threshold=False, output_dir=output_dir)
            if error_msg != "":
                result_df["Errors in Ramp 1s"] = error_msg
            df = result_df
        except Exception as e:
            error_msg = str(e)
            df["Errors in Ramp 1s"] = error_msg
    elif analysis_type == "Ramp 4x":
        try:
            result_df, error_msg = ramp_4x(file_path, df, dvdt, check_ap_counts=False, output_dir=output_dir)
            if error_msg != "":
                result_df["Errors in Ramp 4x"] = error_msg
            df = result_df
        except Exception as e:
            error_msg = str(e)
            df["Errors in Ramp 4x"] = error_msg
    elif analysis_type == "Short Rheo 5ms":
        try:
            result_df, pp5ms, error_msg = short_rheo_5ms(file_path, df, dvdt, check_threshold=False, output_dir=output_dir)
            if error_msg != "":
                result_df["Errors in Short Rheo 5ms"] = error_msg
            df = result_df
        except Exception as e:
            error_msg = str(e)
            df["Errors in Short Rheo 5ms"] = error_msg

    return task, df

def multiprocess(folder_paths, output_dir, dvdt=20, status_label=None, root=None, status_callback=None):
    """Run analysis on multiple ABF files in parallel using multiprocessing.
    
    Parameters
    ----------
    folder_paths : list[str]
        List of folder paths to search for ABF files, one for each protocol type.
    output_dir : str
        Base directory to save the analysis results.
    dvdt : float, optional
        dV/dt threshold used for AP detection, by default 20.
    status_label : tk.Label, optional
        A Tkinter Label widget to display status updates, by default None.
    root : tk.Tk, optional
        The Tkinter root window, used for updating the UI, by default None.
    status_callback : callable, optional
        A callback function for status updates, used for thread-safe UI updates, by default None.
    
    Returns
    -------
    None
    """
    def set_status(text, color="blue"):
        if status_callback is not None:
            status_callback(text, color)
            return
        if status_label is not None:
            status_label.config(text=text, fg=color)
        if root is not None:
            root.update_idletasks()

    print(f"Starting processing at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    tasks = []
    if folder_paths[0] != "No Folder":
        for f in list_abf_files(folder_paths[0]):
            tasks.append({"file_path": f, "protocol": "RMP", "dvdt": dvdt})
    if folder_paths[1] != "No Folder":
        for f in list_abf_files(folder_paths[1]):
            tasks.append({"file_path": f, "protocol": "Rheo 1s", "dvdt": dvdt})
    if folder_paths[2] != "No Folder":
        for f in list_abf_files(folder_paths[2]):
            tasks.append({"file_path": f, "protocol": "Rheo 4x", "dvdt": dvdt})
    if folder_paths[3] != "No Folder":
        for f in list_abf_files(folder_paths[3]):
            tasks.append({"file_path": f, "protocol": "Ramp 1s", "dvdt": dvdt})
    if folder_paths[4] != "No Folder":
        for f in list_abf_files(folder_paths[4]):
            tasks.append({"file_path": f, "protocol": "Ramp 4x", "dvdt": dvdt})
    if folder_paths[5] != "No Folder":
        for f in list_abf_files(folder_paths[5]):
            tasks.append({"file_path": f, "protocol": "Short Rheo 5ms", "dvdt": dvdt})
    length = len(tasks)
    analyzed = 0
    set_status(f"Processed {analyzed}/{length} files...", "blue")

    rmp_results = []
    rheo_1s_results = []
    rheo_4x_results = []
    ramp_1s_results = []
    ramp_4x_results = []
    short_rheo_5ms_results = []

    max_workers = max(1, (os.cpu_count() or 1))
    print("started processing")
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = [executor.submit(run_task, task, output_dir) for task in tasks]
        for future in as_completed(future_to_task):
            task, result_df = future.result()
            if task["protocol"] == "RMP":
                rmp_results.append(result_df)
            elif task["protocol"] == "Rheo 1s":
                rheo_1s_results.append(result_df)
            elif task["protocol"] == "Rheo 4x":
                rheo_4x_results.append(result_df)
            elif task["protocol"] == "Ramp 1s":
                ramp_1s_results.append(result_df)
            elif task["protocol"] == "Ramp 4x":
                ramp_4x_results.append(result_df)
            elif task["protocol"] == "Short Rheo 5ms":
                short_rheo_5ms_results.append(result_df)
            analyzed += 1
            set_status(f"Processed {analyzed}/{length} files...", "blue")
    if rmp_results:
        rmp_df = pd.concat(rmp_results, ignore_index=False, sort=False).sort_index()
        rmp_df.to_csv(os.path.join(output_dir, "RMP_results.csv"))
    if rheo_1s_results:
        rheo_1s_df = pd.concat(rheo_1s_results, ignore_index=False, sort=False).sort_index()
        rheo_1s_df.to_csv(os.path.join(output_dir, "Rheo_1s_results.csv"))
    if rheo_4x_results:
        rheo_4x_df = pd.concat(rheo_4x_results, ignore_index=False, sort=False).sort_index()
        rheo_4x_df.to_csv(os.path.join(output_dir, "Rheo_4x_results.csv"))
    if ramp_1s_results:
        ramp_1s_df = pd.concat(ramp_1s_results, ignore_index=False, sort=False).sort_index()
        ramp_1s_df.to_csv(os.path.join(output_dir, "Ramp_1s_results.csv"))
    if ramp_4x_results:
        ramp_4x_df = pd.concat(ramp_4x_results, ignore_index=False, sort=False).sort_index()
        ramp_4x_df.to_csv(os.path.join(output_dir, "Ramp_4x_results.csv"))
    if short_rheo_5ms_results:
        short_rheo_5ms_df = pd.concat(short_rheo_5ms_results, ignore_index=False, sort=False).sort_index()
        short_rheo_5ms_df.to_csv(os.path.join(output_dir, "Short_Rheo_5ms_results.csv"))
    set_status("Processing Complete!", "green")
    print(f"Finished processing at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
