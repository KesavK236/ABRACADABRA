import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
import sys
from logic.summary import callback
from logic.bulk_summary import bulk_analysis
from logic.nwb_conversion import convert_to_nwb
from config_manager import load_config, save_config
from PIL import ImageTk, Image

filenames = ["No File Chosen"] * 6
foldernames = [""] * 6

def launch_gui(root):
    def make_file_change_handler(index):
        def file_change():
            if process_bool.get():
                foldername = askdirectory()
                if foldername == "":
                    foldername = "No Folder Chosen"
                foldernames[index] = foldername
                file_labels[index].config(text=foldername.split("/")[-1])
            else:
                filename = askopenfilename()
                if filename == "":
                    filename = "No File Chosen"
                filenames[index] = filename
                file_labels[index].config(text=filename.split("/")[-1])
        return file_change
    
    def make_file_clear_handler(index):
        def file_clear():
            if process_bool.get():
                foldernames[index] = "No Folder Chosen"
                file_labels[index].config(text="No Folder Chosen")
            else:
                filenames[index] = "No File Chosen"
                file_labels[index].config(text="No File Chosen")
        return file_clear
    
    
    def apply_mode():
        if not process_bool.get():
            process_bool.set(True)
            process_button.config(image=batch_img)
            # Batch mode
            for i in range(6):
                file_labels[i].config(text="No Folder Chosen")
                filenames[i] = "No Folder Chosen"
            file_labels[0].config(text="No Folder Chosen")
            filenames[0] = "No Folder Chosen"

            for i in range(6):
                change_buttons[i].config(text="Change Folder")
                clear_buttons[i].config(text="Clear Folder")
        else:
            # Single-cell mode
            process_bool.set(False)
            process_button.config(image=single_img)
            for i in range(6):
                file_labels[i].config(text="No File Chosen")
                filenames[i] = "No File Chosen"
            file_labels[0].config(text="No File Chosen")
            filenames[0] = "No File Chosen"

            for i in range(6):
                change_buttons[i].config(text="Change File")
                clear_buttons[i].config(text="Clear File")

    def on_enter():
        run_button.config(state="disabled")
        
        for i in range(6):
            error_labels[i].config(text="")
        root.update_idletasks()
        if process_bool.get():
            status_label.config(text="Running Bulk Analysis...", fg="blue")
            root.update_idletasks()
            try:
                bulk_analysis(
                    folder_paths=foldernames,
                    output_name=output_filename.get(),
                    dvdt=int(dvdt_value.get()),
                    verify_threshold=check_threshold.get(),
                    verify_ap_counts=check_ap_counts.get(),
                    open_excel = open_excel.get(),
                    open_phase = open_phase.get(),
                    status_label= status_label,
                    error_labels= error_labels,
                    root= root
                )
            except Exception as e:
                status_label.config(text=f"Error: {str(e)}", fg="red")
            finally:
                run_button.config(state="normal")
        else:
            status_label.config(text="Running Single-Cell Analysis...", fg="blue")
            root.update_idletasks()
            try:
                callback(
                    file_paths=filenames,
                    output_name=output_filename.get(),
                    dvdt=int(dvdt_value.get()),
                    verify_threshold=check_threshold.get(),
                    verify_ap_counts=check_ap_counts.get(),
                    open_excel = open_excel.get(),
                    open_phase = open_phase.get(),
                    status_label= status_label,
                    error_labels= error_labels,
                    root= root
                )
            except Exception as e:
                status_label.config(text=f"Error: {str(e)}", fg="red")
            finally:
                run_button.config(state="normal")

    def on_convert():
        convert_button.config(state="disabled")
        status_label.config(text="Converting to NWB...", fg="blue")
        for i in range(6):
            error_labels[i].config(text="")
        root.update_idletasks()
        try:
            convert_to_nwb(file_names=filenames, output_folder=output_filename.get())
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}", fg="red")
        else:
            status_label.config(text="NWB Conversion Complete!", fg="green")
        finally:
            convert_button.config(state="normal")


    def on_closing():
        root.destroy()
        config["dvdt_value"] = dvdt_value.get()
        config["check_threshold"] = check_threshold.get()
        config["check_ap_counts"] = check_ap_counts.get()
        config["open_excel"] = open_excel.get()
        config["open_phase"] = open_phase.get()
        save_config(config)
        sys.exit()

    config = load_config()


    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Title
    label_title = tk.Label(root, text="ABRACADABRA", font=("Verdana", 20))
    label_title.grid(row=0, column=0, columnspan=6, pady=10, sticky='n')

    # single/ batch toggle
    single_label = tk.Label(root, text="Single-Cell Extraction", font=("Verdana", 14))
    batch_label = tk.Label(root, text="Batch Extraction", font=("Verdana", 14))
    single_label.grid(row=1, column=1, columnspan=2, pady=5, sticky='e')
    batch_label.grid(row=1, column=4, pady=5, sticky='w')

    single_img_temp = Image.open("assets/single_switch.png")
    single_img_temp = single_img_temp.resize((65,26), Image.LANCZOS)
    single_img = ImageTk.PhotoImage(single_img_temp)

    batch_img_temp = Image.open("assets/batch_switch.png")
    batch_img_temp = batch_img_temp.resize((65,26), Image.LANCZOS)
    batch_img = ImageTk.PhotoImage(batch_img_temp)

    
    process_bool = tk.BooleanVar(value=False)
    process_button = tk.Button(root, image= single_img, bd = 0, command=apply_mode)
    process_button.image = single_img     
    process_button.grid(row=1, column=3, pady=15)            

    # File input labels and buttons
    protocols = ["RMP", "Rheo 1s", "Rheo 4x", "Ramp 1s", "Ramp 4x", "Rheo 5ms"]
    file_labels = []
    error_labels = []
    clear_buttons = []
    change_buttons = []
    for i in range(6):
        button_clear = tk.Button(root, text="Clear File", font=("Verdana", 12), bg="grey", fg="black", command=make_file_clear_handler(i))
        clear_buttons.append(button_clear)
        button_clear.grid(row=i+2, column=0, padx=15, sticky='w')

        label_text = protocols[i]
        label = tk.Label(root, text=label_text, font=("Verdana", 12))
        label.grid(row=i+2, column=1, padx=(220, 6), sticky='e')

        spacer = tk.Label(root, text=" ")  # empty column to center the gap
        spacer.grid(row=i+2, column=2, padx=0, pady=10)

        button_change = tk.Button(root, text="Change File", font=("Verdana", 12), bg="grey", fg="black", command=make_file_change_handler(i))
        change_buttons.append(button_change)
        button_change.grid(row=i+2, column=3, padx=5, sticky='n')

        file_label = tk.Label(root, text="No File Chosen", font=("Verdana", 12), anchor="w", width=30)
        file_label.grid(row=i+2, column=4, sticky='w', padx=15)
        file_labels.append(file_label)

        error_label = tk.Label(root, text="", font=("Verdana", 12), anchor="w", fg="red")
        error_label.grid(row=i+2, column=5, columnspan=2, padx=15)
        error_labels.append(error_label)

    # Spinbox and checkbuttons
    dvdt_label = tk.Label(root, text="Threshold dV/dt (mV/ms):", font=("Verdana", 12))
    dvdt_label.grid(row=9, column=0, columnspan=2, sticky="e", pady=10)

    dvdt_value = tk.StringVar(value="10")
    if "dvdt_value" in config:
        dvdt_value.set(int(config["dvdt_value"]))
    spinbox_dvdt = tk.Spinbox(root, from_=1, to=100, width=5, textvariable=dvdt_value, font=("Verdana", 12))
    spinbox_dvdt.grid(row=9, column=3)

    check_threshold = tk.BooleanVar()
    if "check_threshold" in config:
        check_threshold.set(bool(config["check_threshold"]))
    threshold_check = tk.Checkbutton(root, text="Verify Threshold Value", font=("Verdana", 12), variable=check_threshold)
    threshold_check.grid(row=10, column=2, columnspan=3, sticky='w')

    check_ap_counts = tk.BooleanVar()
    if "check_ap_counts" in config:
        check_ap_counts.set(bool(config["check_ap_counts"]))
    ap_count_check = tk.Checkbutton(root, text="Verify AP Counts", font=("Verdana", 12), variable=check_ap_counts)
    ap_count_check.grid(row=11, column=2, columnspan=3, sticky='w')

    open_excel = tk.BooleanVar(value=True)
    if "open_excel" in config:
        open_excel.set(bool(config["open_excel"]))
    open_excel_check = tk.Checkbutton(root, text="Open Analysis after analysis", font=("Verdana", 12), variable=open_excel)
    open_excel_check.grid(row=12, column=2, columnspan=3, sticky='sw', pady=10)

    open_phase = tk.BooleanVar()
    if "open_phase" in config:
        open_phase.set(bool(config["open_phase"]))
    open_phase_check = tk.Checkbutton(root, text="Open Phase Plane after analysis", font=("Verdana", 12), variable=open_phase)
    open_phase_check.grid(row=13, column=2, columnspan=3, sticky='w')

    # Output Stuff
    output_label = tk.Label(root, text="Output File Name", font=("Verdana", 14))
    output_label.grid(row=14, column=0, columnspan=6, sticky='s')
    output_filename = tk.StringVar()
    output_entry = tk.Entry(root, textvariable=output_filename, width=40, justify="center", font=("Verdana", 12))
    output_entry.grid(row=15, column=0, columnspan=6, sticky='s')

    run_button = tk.Button(root, text="Enter", width=15, bg="green", fg="black", font=("Verdana", 12), command=on_enter)
    run_button.grid(row=16, column=0, columnspan=6, pady=10, sticky='s')

    status_label = tk.Label(root, text="", fg="blue", font=("Verdana", 14), wraplength=1000)
    status_label.grid(row=18, column=0, columnspan=6)

    convert_button = tk.Button(root, text="Convert to NWB", width=15, bg="orange", fg="black", font=("Verdana", 12), command=on_convert)
    convert_button.grid(row=17, column=0, columnspan=6, pady=5, sticky='s')


    # Adding weight to rows and columns
    root.grid_columnconfigure(0, weight=0, minsize= 143)
    root.grid_columnconfigure(1, weight=0)  
    root.grid_columnconfigure(2, weight=0)  
    root.grid_columnconfigure(3, weight=0, minsize= 142)  
    root.grid_columnconfigure(4, weight=0, minsize= 429)
    root.grid_columnconfigure(5, weight=0, minsize= 36)
    root.grid_columnconfigure(6, weight=1)

    root.grid_rowconfigure(10, weight=1)
    root.grid_rowconfigure(12, weight=0)
    root.grid_rowconfigure(13, weight=0)
