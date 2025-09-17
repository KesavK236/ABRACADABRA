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

def callback(file_paths, output_name, dvdt, verify_threshold = False, verify_ap_counts = False, open_excel = False, open_phase = False, status_label  = None, root = None):
    if not output_name:
        raise ValueError("Output file name cannot be empty.")

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
            if root != None:
                status_label.config(text="Running RMP Protocol...", fg="blue")
                root.update_idletasks()
            output_df = rmp(file_paths[0], output_df, output_dir)
        except:
            error_msg = "error in RMP file"
    if file_paths[1] != no_file:
        try:
            if root != None:
                status_label.config(text="Running Rheo 1s Protocol...", fg="blue")
                root.update_idletasks()
            output_df, pp_1s = short_rheo_1s(file_paths[1], output_df, dvdt, verify_threshold, output_dir)
        except:
            error_msg = "error in Rheo 1s file"
    if file_paths[2] != no_file:
        try:
            if root != None:
                status_label.config(text="Running Rheo 4x Protocol...", fg="blue")
                root.update_idletasks()
            output_df = rheo_4x(file_paths[2], output_df, dvdt, verify_ap_counts, output_dir)
        except:
            error_msg = "error in Rheo 4x file"
    if file_paths[3] != no_file:
        try:
            if root != None:
                status_label.config(text="Running Ramp 1s Protocol...", fg="blue")
                root.update_idletasks()
            output_df = ramp_1s(file_paths[3], output_df, dvdt, verify_threshold, output_dir)
        except:
            error_msg = "error in Ramp 1s file"
    if file_paths[4] != no_file:
        try:
            if root != None:
                status_label.config(text="Running Ramp 4x Protocol...", fg="blue")
                root.update_idletasks()
            output_df = ramp_4x(file_paths[4], output_df, dvdt, verify_ap_counts, output_dir)
        except:
            error_msg = "error in Ramp 4x file"
    if file_paths[5] != no_file:
        try:
            if root != None:
                status_label.config(text="Running Single AP 5ms...", fg="blue")
                root.update_idletasks()
            output_df, pp_5ms = short_rheo_5ms(file_paths[5], output_df, dvdt, verify_threshold, output_dir)
        except:
            error_msg = "error in Single AP 5ms file"

    version = 2.1

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
        status_label.config(text="Analysis complete.", fg="green")
        root.update_idletasks()
    else:
        status_label.config(text=error_msg, fg="red")
        root.update_idletasks()

    return output_path