import os
import tkinter as tk
import threading
import queue
from tkinter.filedialog import askopenfilename, askdirectory
import sys
from logic.summary import callback
from logic.nwb_conversion import convert_to_nwb
from config_manager import load_config, save_config
from logic.multiprocess import multiprocess
from PIL import ImageTk, Image

def resource_path(relative_path):
    """Resolve an asset path for source and PyInstaller builds.

    Parameters
    ----------
    relative_path : str
        Relative path from the project (or bundled app) root.

    Returns
    -------
    str
        Absolute path to the requested resource.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)



filenames = ["No File Chosen"] * 6
foldernames = [""] * 6

def launch_gui(root):
    """Build and launch the ABRACADABRA Tkinter interface.

    Parameters
    ----------
    root : tkinter.Tk
        Root Tkinter window.
    """
    ui_queue = queue.Queue()

    def invoke_on_main_thread(fn, *args, **kwargs):
        """Run a callable on the Tk main thread and block for its result.

        Parameters
        ----------
        fn : callable
            Function to execute on the main thread.
        *args : tuple
            Positional arguments forwarded to ``fn``.
        **kwargs : dict
            Keyword arguments forwarded to ``fn``.

        Returns
        -------
        object
            Return value from ``fn``.
        """
        if threading.current_thread() is threading.main_thread():
            return fn(*args, **kwargs)

        done = threading.Event()
        result = {"value": None, "error": None}

        def runner():
            try:
                result["value"] = fn(*args, **kwargs)
            except Exception as e:
                result["error"] = e
            finally:
                done.set()

        root.after(0, runner)
        done.wait()
        if result["error"] is not None:
            raise result["error"]
        return result["value"]

    def schedule_status(text, color="blue"):
        """Queue a status-label update for main-thread processing.

        Parameters
        ----------
        text : str
            Status message text.
        color : str, optional
            Tk-compatible foreground color. Default is ``"blue"``.
        """
        ui_queue.put(("status", text, color))

    def schedule_error(index, text):
        """Queue a protocol error-label update for main-thread processing.

        Parameters
        ----------
        index : int
            Protocol row index in the UI.
        text : str
            Error message text.
        """
        ui_queue.put(("error", index, text))

    def schedule_done(button, message=None, color="green"):
        """Queue completion UI updates for a finished background task.

        Parameters
        ----------
        button : tkinter.Button
            Button to re-enable after task completion.
        message : str, optional
            Optional status message to display.
        color : str, optional
            Status color used when ``message`` is provided.
        """
        ui_queue.put(("done", button, message, color))

    def schedule_failure(button, message):
        """Queue failure UI updates for a background task.

        Parameters
        ----------
        button : tkinter.Button
            Button to re-enable after failure.
        message : str
            Error message text.
        """
        ui_queue.put(("failure", button, message))

    def process_ui_queue():
        """Drain queued UI events and apply them on the Tk thread.
        """
        try:
            while True:
                event = ui_queue.get_nowait()
                event_type = event[0]
                if event_type == "status":
                    _, text, color = event
                    status_label.config(text=text, fg=color)
                elif event_type == "error":
                    _, index, text = event
                    error_labels[index].config(text=text)
                elif event_type == "done":
                    _, button, message, color = event
                    if message:
                        status_label.config(text=message, fg=color)
                    button.config(state="normal")
                elif event_type == "failure":
                    _, button, message = event
                    status_label.config(text=f"Error: {message}", fg="red")
                    button.config(state="normal")
        except queue.Empty:
            pass
        root.after(100, process_ui_queue)

    def start_background_task(button, worker):
        """Start a worker thread and manage button/UI completion state.

        Parameters
        ----------
        button : tkinter.Button
            Button disabled during task execution and re-enabled at exit.
        worker : callable
            Zero-argument callable executed in a daemon thread.

        """
        button.config(state="disabled")

        def run_worker():
            try:
                worker()
                schedule_done(button)
            except Exception as e:
                schedule_failure(button, str(e))

        threading.Thread(target=run_worker, daemon=True).start()

    def make_file_change_handler(index):
        """Build a file/folder picker callback bound to a protocol index.

        Parameters
        ----------
        index : int
            Protocol row index.

        Returns
        -------
        callable
            UI callback for the corresponding Change button.
        """
        def file_change():
            """Handle Change button selection for one protocol row.
            """
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
        """Build a clear callback bound to a protocol index.

        Parameters
        ----------
        index : int
            Protocol row index.

        Returns
        -------
        callable
            UI callback for the corresponding Clear button.
        """
        def file_clear():
            """Handle Clear button behavior for one protocol row.
            """
            if process_bool.get():
                foldernames[index] = "No Folder Chosen"
                file_labels[index].config(text="No Folder Chosen")
            else:
                filenames[index] = "No File Chosen"
                file_labels[index].config(text="No File Chosen")
        return file_clear
    
    
    def apply_mode():
        """Toggle between single-cell and batch-processing UI modes.
        """
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
        """Start analysis using current UI selections and mode.
        """
        for i in range(6):
            error_labels[i].config(text="")
        if process_bool.get():
            status_label.config(text="Running Bulk Analysis...", fg="blue")

            folder_paths = list(foldernames)
            output_dir = output_filename.get()
            dvdt = int(dvdt_value.get())

            def bulk_worker():
                """Execute bulk analysis work in a worker thread.
                """
                # bulk_analysis(...) is intentionally left disabled here to preserve existing behavior.
                multiprocess(
                    folder_paths=folder_paths,
                    output_dir=output_dir,
                    dvdt=dvdt,
                    status_callback=schedule_status
                )

            start_background_task(run_button, bulk_worker)
        else:
            status_label.config(text="Running Single-Cell Analysis...", fg="blue")

            file_paths = list(filenames)
            output_name = output_filename.get()
            dvdt = int(dvdt_value.get())
            verify_threshold_value = check_threshold.get()
            verify_ap_counts_value = check_ap_counts.get()
            open_excel_value = open_excel.get()
            open_phase_value = open_phase.get()

            def single_worker():
                """Execute single-cell analysis work in a worker thread.
                """
                callback(
                    file_paths=file_paths,
                    output_name=output_name,
                    dvdt=dvdt,
                    verify_threshold=verify_threshold_value,
                    verify_ap_counts=verify_ap_counts_value,
                    open_excel=open_excel_value,
                    open_phase=open_phase_value,
                    status_callback=schedule_status,
                    error_callback=schedule_error,
                    threshold_window_callback=invoke_on_main_thread,
                    ap_count_window_callback=invoke_on_main_thread
                )

            start_background_task(run_button, single_worker)

    def on_convert():
        """Start NWB conversion for selected files.
        """
        for i in range(6):
            error_labels[i].config(text="")
        status_label.config(text="Converting to NWB...", fg="blue")

        file_names = list(filenames)
        output_folder = output_filename.get()

        def convert_worker():
            """Execute NWB conversion in a worker thread.
            """
            convert_to_nwb(file_names=file_names, output_folder=output_folder)
            schedule_status("NWB Conversion Complete!", "green")

        start_background_task(convert_button, convert_worker)


    def on_closing():
        """Persist config and close the application window.
        """
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
    
    single_img_path = resource_path("assets/single_switch.png")
    single_img_temp = Image.open(single_img_path)
    single_img_temp = single_img_temp.resize((65,26), Image.LANCZOS)
    single_img = ImageTk.PhotoImage(single_img_temp)

    batch_img_path = resource_path("assets/batch_switch.png")
    batch_img_temp = Image.open(batch_img_path)
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

    process_ui_queue()
