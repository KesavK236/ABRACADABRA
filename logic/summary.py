from logic.rmp import rmp
from logic.rheo_1s import rheo_1s
from logic.rheo_4x import rheo_4x
from logic.ramp_1s import ramp_1s
from logic.ramp_4x import ramp_4x
from logic.short_rheo_5ms import short_rheo_5ms
from logic.short_rheo_1s import short_rheo_1s
import os

def callback(file_paths, output_name, dvdt, verify_threshold = False, verify_ap_counts = False, open_excel = False, open_phase = False, status_label  = None, root = None):
    if not output_name:
        raise ValueError("Output file name cannot be empty.")

    # Create output directory
    folder_name = output_name + "_outputs"
    output_dir = os.path.join(os.getcwd(), folder_name)
    os.makedirs(output_dir, exist_ok=True)

    error_msg = ""
    output_path = os.path.join(output_dir, output_name + "_analyzed.csv")
    no_file = "No File Chosen"
    with open(output_path, "w") as f:
        if file_paths[0] != no_file:
            try:
                if root != None:
                    status_label.config(text="Running RMP Protocol...", fg="blue")
                    root.update_idletasks()
                rmp(file_paths[0], f)
            except:
                error_msg = "error in RMP file"
        if file_paths[1] != no_file:
            try:
                if root != None:
                    status_label.config(text="Running Rheo 1s Protocol...", fg="blue")
                    root.update_idletasks()
                rheo_1s(file_paths[1], f, dvdt)
            except:
                error_msg = "error in Rheo 1s file"
        if file_paths[2] != no_file:
            try:
                if root != None:
                    status_label.config(text="Running Rheo 4x Protocol...", fg="blue")
                    root.update_idletasks()
                rheo_4x(file_paths[2], f, dvdt, verify_ap_counts)
            except:
                error_msg = "error in Rheo 4x file"
        if file_paths[3] != no_file:
            try:
                if root != None:
                    status_label.config(text="Running Ramp 1s Protocol...", fg="blue")
                    root.update_idletasks()
                ramp_1s(file_paths[3], f, dvdt, verify_threshold)
            except:
                error_msg = "error in Ramp 1s file"
        if file_paths[4] != no_file:
            try:
                if root != None:
                    status_label.config(text="Running Ramp 4x Protocol...", fg="blue")
                    root.update_idletasks()
                ramp_4x(file_paths[4], f, dvdt, verify_ap_counts)
            except:
                error_msg = "error in Ramp 4x file"
        if file_paths[5] != no_file:
            try:
                if root != None:
                    status_label.config(text="Running Single AP 5ms...", fg="blue")
                    root.update_idletasks()
                pp_5ms = short_rheo_5ms(file_paths[5], f, dvdt, verify_threshold)
            except:
                error_msg = "error in Single AP 5ms file"
        if file_paths[6] != no_file:
            try:
                if root != None:
                    status_label.config(text="Running Single AP 1s...", fg="blue")
                    root.update_idletasks()
                pp_1s = short_rheo_1s(file_paths[6], f, dvdt, verify_threshold)
            except:
                error_msg = "error in Single AP 1s file"
    
        version = 2.1

        print(f"ABRACADABRA Version: {version}")
        f.write(f"ABRACADABRA Version:, {version}\n")
    
    
    if open_excel:
        os.system("start EXCEL.EXE " + output_path)

    if open_phase:
        if file_paths[5] != no_file:
            os.system("start EXCEL.EXE " + pp_5ms)
        if file_paths[6] != no_file:
            os.system("start EXCEL.EXE " + pp_1s)
    
    if error_msg == "":
        status_label.config(text="Analysis complete.", fg="green")
        root.update_idletasks()
    else:
        status_label.config(text=error_msg, fg="red")
        root.update_idletasks()

    return output_path