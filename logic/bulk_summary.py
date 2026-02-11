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

def bulk_analysis(folder_paths, output_name, dvdt, verify_threshold = False, verify_ap_counts = False, open_excel = False, open_phase = False, status_label  = None, error_labels = None, root = None):
    if not output_name:
        raise ValueError("Output file name cannot be empty.")

    no_folder = "No Folder Chosen"

    # Create output directory
    folder_name = output_name + "_outputs"
    output_dir = os.path.join(os.getcwd(), folder_name)
    os.makedirs(output_dir, exist_ok=True)
    
    # create output df

    error_msg = ""
    output_path = os.path.join(output_dir, output_name + "_analyzed.csv")

    if folder_paths[0] != no_folder:
        rmp_df = pd.DataFrame()
        tempelet_df = rmp_df.copy()
        for root_dir, _, filenames in os.walk(folder_paths[0]):
            for f in filenames:
                path = os.path.join(root_dir, f)
                if re.search(r'\.abf$', f, re.IGNORECASE):
                    
                    temp_df = tempelet_df.copy()
                    temp_df.index = [os.path.basename(f)]
                    try:
                        if root != None:
                            status_label.config(text=f"Running RMP Protocol on {f}...", fg="blue")
                            root.update_idletasks()
                        
                        rmp_single_df, error_msg = rmp(path, temp_df, output_dir)
                        if error_msg != "":
                            rmp_single_df["Errors in RMP"] = error_msg
                        rmp_df = pd.concat([rmp_df, rmp_single_df], ignore_index=False, sort=False).sort_index()
                        root.update_idletasks()
                    except Exception as e:
                        rmp_single_df["Errors in RMP"] = str(e)
                        rmp_df = pd.concat([rmp_df, temp_df], ignore_index=False, sort=False).sort_index()
                        root.update_idletasks()
            rmp_df = rmp_df.to_csv(os.path.join(output_dir, output_name + "_RMP_results.csv"))
    if folder_paths[1] != no_folder:
        rheo1s_df = pd.DataFrame()
        tempelet_df = rheo1s_df.copy()
        for root_dir, _, filenames in os.walk(folder_paths[1]):
            for f in filenames:
                path = os.path.join(root_dir, f)
                if re.search(r'\.abf$', f, re.IGNORECASE):
                    temp_df = tempelet_df.copy()
                    temp_df.index = [os.path.basename(f)]
                    try:
                        if root != None:
                            status_label.config(text=f"Running Rheo 1s Protocol on {f}...", fg="blue")
                            root.update_idletasks()
                        
                        rheo1s_single_df, pp1s, error_msg = short_rheo_1s(path, temp_df, dvdt, verify_threshold, output_dir)
                        if error_msg != "":
                            rheo1s_single_df["Errors in Rheo 1s"] = error_msg
                        rheo1s_df = pd.concat([rheo1s_df, rheo1s_single_df], ignore_index=False, sort=False).sort_index()
                        root.update_idletasks()
                    except Exception as e:
                        rheo1s_single_df["Errors in Rheo 1s"] = str(e)
                        rheo1s_df = pd.concat([rheo1s_df, temp_df], ignore_index=False, sort=False).sort_index()
                        root.update_idletasks()
        rheo1s_df = rheo1s_df.to_csv(os.path.join(output_dir, output_name + "_Rheo_1s_results.csv"))
    
    if folder_paths[2] != no_folder:
        rheo4x_df = pd.DataFrame()
        tempelet_df = rheo4x_df.copy()
        for root_dir, _, filenames in os.walk(folder_paths[2]):
            for f in filenames:
                path = os.path.join(root_dir, f)
                if re.search(r'\.abf$', f, re.IGNORECASE):
                    temp_df = tempelet_df.copy()
                    temp_df.index = [os.path.basename(f)]
                    try:
                        if root != None:
                            status_label.config(text=f"Running Rheo 4x Protocol on {f}...", fg="blue")
                            root.update_idletasks()
                        
                        rheo4x_single_df, error_msg = rheo_4x(path, temp_df, dvdt, verify_ap_counts, output_dir)
                        if error_msg != "":
                            rheo4x_single_df["Errors in Rheo 4x"] = error_msg
                        rheo4x_df = pd.concat([rheo4x_df, rheo4x_single_df], ignore_index=False, sort=False).sort_index()
                        root.update_idletasks()
                    except Exception as e:
                        rheo4x_single_df["Errors in Rheo 4x"] = str(e)
                        rheo4x_df = pd.concat([rheo4x_df, temp_df], ignore_index=False, sort=False).sort_index()
                        root.update_idletasks()
        rheo4x_df = rheo4x_df.to_csv(os.path.join(output_dir, output_name + "_Rheo_4x_results.csv"))

    if folder_paths[3] != no_folder:
        ramp1s_df = pd.DataFrame()
        tempelet_df = ramp1s_df.copy()
        for root_dir, _, filenames in os.walk(folder_paths[3]):
            for f in filenames:
                path = os.path.join(root_dir, f)
                if re.search(r'\.abf$', f, re.IGNORECASE):
                    temp_df = tempelet_df.copy()
                    temp_df.index = [os.path.basename(f)]
                    try:
                        if root != None:
                            status_label.config(text=f"Running Ramp 1s Protocol on {f}...", fg="blue")
                            root.update_idletasks()
                        
                        ramp1s_single_df, error_msg = ramp_1s(path, temp_df, dvdt, verify_threshold, output_dir)
                        if error_msg != "":
                            ramp1s_single_df["Errors in Ramp 1s"] = error_msg
                        ramp1s_df = pd.concat([ramp1s_df, ramp1s_single_df], ignore_index=False, sort=False).sort_index()
                        root.update_idletasks()
                    except Exception as e:
                        ramp1s_single_df["Errors in Ramp 1s"] = str(e)
                        ramp1s_df = pd.concat([ramp1s_df, ramp1s_single_df], ignore_index=False, sort=False).sort_index()
                        root.update_idletasks()
        ramp1s_df = ramp1s_df.to_csv(os.path.join(output_dir, output_name + "_Ramp_1s_results.csv"))
    

    if folder_paths[4] != no_folder:
        ramp4x_df = pd.DataFrame()
        tempelet_df = ramp4x_df.copy()
        for root_dir, _, filenames in os.walk(folder_paths[4]):
            for f in filenames:
                path = os.path.join(root_dir, f)
                if re.search(r'\.abf$', f, re.IGNORECASE):
                    temp_df = tempelet_df.copy()
                    temp_df.index = [os.path.basename(f)]
                    try:
                        if root != None:
                            status_label.config(text=f"Running Ramp 4x Protocol on {f}...", fg="blue")
                            root.update_idletasks()
                        
                        ramp4x_single_df, error_msg = ramp_4x(path, temp_df, dvdt, verify_ap_counts, output_dir)
                        if error_msg != "":
                            ramp4x_single_df["Errors in Ramp 4x"] = error_msg
                        ramp4x_df = pd.concat([ramp4x_df, ramp4x_single_df], ignore_index=False, sort=False).sort_index()
                        root.update_idletasks()
                    except Exception as e:
                        ramp4x_single_df["Errors in Ramp 4x"] = str(e)
                        ramp4x_df = pd.concat([ramp4x_df, ramp4x_single_df], ignore_index=False, sort=False).sort_index()
                        root.update_idletasks()
        ramp4x_df = ramp4x_df.to_csv(os.path.join(output_dir, output_name + "_Ramp_4x_results.csv"))

    if folder_paths[5] != no_folder:
        rheo5ms_df = pd.DataFrame()
        tempelet_df = rheo5ms_df.copy()
        for root_dir, _, filenames in os.walk(folder_paths[5]):
            for f in filenames:
                path = os.path.join(root_dir, f)
                if re.search(r'\.abf$', f, re.IGNORECASE):
                    temp_df = tempelet_df.copy()
                    temp_df.index = [os.path.basename(f)]
                    try:
                        if root != None:
                            status_label.config(text=f"Running Rheo 5ms Protocol on {f}...", fg="blue")
                            root.update_idletasks()
                        
                        rheo5ms_single_df, pp5ms, error_msg = short_rheo_5ms(path, temp_df, dvdt, verify_threshold, output_dir)
                        if error_msg != "":
                            rheo5ms_single_df["Errors in Rheo 5ms"] = error_msg
                        rheo5ms_df = pd.concat([rheo5ms_df, rheo5ms_single_df], ignore_index=False, sort=False).sort_index()
                        root.update_idletasks()
                    except Exception as e:
                        rheo5ms_single_df["Errors in Rheo 5ms"] = str(e)
                        rheo5ms_df = pd.concat([rheo5ms_df, rheo5ms_single_df], ignore_index=False, sort=False).sort_index()
                        root.update_idletasks()
        rheo5ms_df = rheo5ms_df.to_csv(os.path.join(output_dir, output_name + "_Rheo_5ms_results.csv"))
    
    status_label.config(text="Analysis complete.", fg="green")
    root.update_idletasks()
    