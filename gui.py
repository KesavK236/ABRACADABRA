import tkinter as tk
from tkinter.filedialog import askopenfilename
import sys
from logic.summary import callback

filenames = ["No File Chosen"] * 6

def launch_gui(root):
    def make_file_change_handler(index):
        def file_change():
            filename = askopenfilename()
            if filename == "":
                filename = "No File Chosen"
            filenames[index] = filename
            file_labels[index].config(text=filename.split("/")[-1])
        return file_change
    
    def make_file_clear_handler(index):
        def file_clear():
            filenames[index] = "No File Chosen"
            file_labels[index].config(text="No File Chosen")
        return file_clear
    
    def on_enter():
        run_button.config(state="disabled")
        status_label.config(text="Running analysis...", fg="blue")
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
                root= root
            )
            
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}", fg="red")
        finally:
            run_button.config(state="normal")

    def on_closing():
        root.destroy()
        sys.exit()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Title
    label_title = tk.Label(root, text="ABRACADABRA", font=("Verdana", 20))
    label_title.grid(row=0, column=0, columnspan=6, pady=10, sticky='n')

    # File input labels and buttons
    protocols = ["RMP", "Rheo 1s", "Rheo 4x", "Ramp 1s", "Ramp 4x", "Rheo 5ms Single AP"]
    file_labels = []
    for i in range(6):
        button_clear = tk.Button(root, text="Clear File", font=("Verdana", 12), bg="grey", fg="black", command=make_file_clear_handler(i))
        button_clear.grid(row=i+1, column=0, padx=15, sticky='w')

        label_text = protocols[i]
        label = tk.Label(root, text=label_text, font=("Verdana", 12))
        label.grid(row=i+1, column=1, sticky='e')

        spacer = tk.Label(root, text=" ")  # empty column to center the gap
        spacer.grid(row=i+1, column=2, padx=0, pady=10)

        button_change = tk.Button(root, text="Change File", font=("Verdana", 12), bg="grey", fg="black", command=make_file_change_handler(i))
        button_change.grid(row=i+1, column=3, padx=5, sticky='w')

        file_label = tk.Label(root, text="No File Chosen", font=("Verdana", 12), anchor="w", width=30)
        file_label.grid(row=i+1, column=4)
        file_labels.append(file_label)

    # Spinbox and checkbuttons
    dvdt_label = tk.Label(root, text="Threshold dV/dt (mV/ms):", font=("Verdana", 12))
    dvdt_label.grid(row=8, column=0, columnspan=2, sticky="e", pady=10)

    dvdt_value = tk.StringVar(value="10")
    spinbox_dvdt = tk.Spinbox(root, from_=1, to=100, width=5, textvariable=dvdt_value, font=("Verdana", 12))
    spinbox_dvdt.grid(row=8, column=3, sticky="w")

    check_threshold = tk.BooleanVar()
    threshold_check = tk.Checkbutton(root, text="Verify Threshold Value", font=("Verdana", 12), variable=check_threshold)
    threshold_check.grid(row=9, column=2, columnspan=3, sticky='w')

    check_ap_counts = tk.BooleanVar()
    ap_count_check = tk.Checkbutton(root, text="Verify AP Counts", font=("Verdana", 12), variable=check_ap_counts)
    ap_count_check.grid(row=10, column=2, columnspan=3, sticky='w')

    open_excel = tk.BooleanVar(value=True)
    open_excel_check = tk.Checkbutton(root, text="Open Analysis after analysis", font=("Verdana", 12), variable=open_excel)
    open_excel_check.grid(row=11, column=2, columnspan=3, sticky='sw', pady=10)

    open_phase = tk.BooleanVar()
    open_phase_check = tk.Checkbutton(root, text="Open Phase Plane after analysis", font=("Verdana", 12), variable=open_phase)
    open_phase_check.grid(row=12, column=2, columnspan=3, sticky='w')

    # Output Stuff
    output_label = tk.Label(root, text="Output File Name", font=("Verdana", 14))
    output_label.grid(row=13, column=0, columnspan=6, sticky='s')
    output_filename = tk.StringVar()
    output_entry = tk.Entry(root, textvariable=output_filename, width=40, justify="center", font=("Verdana", 12))
    output_entry.grid(row=14, column=0, columnspan=6, sticky='s')

    run_button = tk.Button(root, text="Enter", width=10, bg="green", fg="black", font=("Verdana", 12), command=on_enter)
    run_button.grid(row=15, column=0, columnspan=6, pady=10, sticky='s')

    status_label = tk.Label(root, text="", fg="blue", font=("Verdana", 14))
    status_label.grid(row=16, column=0, columnspan=6)


    # Adding weight to rows and columns
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)  
    root.grid_columnconfigure(2, weight=0)  
    root.grid_columnconfigure(3, weight=1)  
    root.grid_columnconfigure(4, weight=1)

    root.grid_rowconfigure(11, weight=1)
    root.grid_rowconfigure(12, weight=0)
    root.grid_rowconfigure(13, weight=0)
