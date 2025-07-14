from logic.rmp import rmp
from logic.rheo_1s import rheo_1s
from logic.rheo_4x import rheo_4x
from logic.ramp_1s import ramp_1s
from logic.ramp_4x import ramp_4x
from logic.short_rheo_5ms import short_rheo_5ms
from logic.short_rheo_1s import short_rheo_1s
import os

def callback(file_paths, output_name, dvdt, verify_threshold, verify_ap_counts, open_excel, open_phase):
    if not output_name:
        raise ValueError("Output file name cannot be empty.")

    # Create output directory
    folder_name = output_name + "_outputs"
    output_dir = os.path.join(os.getcwd(), folder_name)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, output_name + "_analyzed.csv")
    no_file = "No File Chosen"
    with open(output_path, "w") as f:
        if file_paths[0] != no_file:
            rmp(file_paths[0], f)
        if file_paths[1] != no_file:
            rheo_1s(file_paths[1], f, dvdt)
        if file_paths[2] != no_file:
            rheo_4x(file_paths[2], f, dvdt, verify_ap_counts)
        if file_paths[3] != no_file:
            ramp_1s(file_paths[3], f, dvdt, verify_threshold)
        if file_paths[4] != no_file:
            ramp_4x(file_paths[4], f, dvdt, verify_ap_counts)
        if file_paths[5] != no_file:
            pp_5ms = short_rheo_5ms(file_paths[5], f, dvdt, verify_threshold)
        if file_paths[6] != no_file:
            pp_1s = short_rheo_1s(file_paths[6], f, dvdt, verify_threshold)
    
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
    
    # Optional: return path or success message
    return output_path