import tkinter as tk
import sys
import os

def nwb_conversion_input_window():
    global metadata
    convert_window = tk.Toplevel()
    convert_window.title("ABRACADABRA: NWB Conversion")


    def on_enter():
        global metadata
        metadata = {
            "cell_id": cell_id.get(),
            "slice_id": slice_id.get(),
            "targeted_layer": targeted_layer.get(),
            "inferred_layer": inferred_layer.get(),
            "session_description": session_description.get(),
            "lab": lab.get(),
            "institution": institution.get(),
            "experimenter": experimenter.get(),
            "subject_id": subject_id.get(),
            "species": species.get(),
            "sex": sex.get(),
            "date_of_birth": date_of_birth.get() +"T00:00:00",
            "NWB_file_name": nwb_name.get() + ".nwb"
        }
        convert_window.destroy()

    title_label = tk.Label(convert_window, text="NWB Conversion Metadata", font=('Verdana', 16))
    title_label.grid(row=0, column=0, columnspan=2)

    cell_id = tk.StringVar()
    slice_id = tk.StringVar()
    targeted_layer = tk.StringVar()
    inferred_layer = tk.StringVar()
    session_description = tk.StringVar()
    lab = tk.StringVar()
    institution = tk.StringVar()
    institution.set("Washington University in St. Louis")
    experimenter = tk.StringVar()
    subject_id = tk.StringVar()
    species = tk.StringVar()
    species.set("Homo sapiens")
    sex = tk.StringVar()
    date_of_birth = tk.StringVar()
    nwb_name = tk.StringVar()

    label_cell_id = tk.Label(convert_window, text="Cell ID:", font=('Verdana', 12))
    label_cell_id.grid(row=1, column=0)

    entry_cell_id = tk.Entry(convert_window, textvariable=cell_id, font=('Verdana', 12), width= 30)
    entry_cell_id.grid(row=1, column=1)

    label_slice_id = tk.Label(convert_window, text="Slice ID:", font=('Verdana', 12))
    label_slice_id.grid(row=2, column=0)

    entry_slice_id = tk.Entry(convert_window, textvariable=slice_id, font=('Verdana', 12), width= 30)
    entry_slice_id.grid(row = 2, column=1)

    label_targeted_layer = tk.Label(convert_window, text="Targeted Layer:", font=('Verdana', 12))
    label_targeted_layer.grid(row=3, column=0)

    entry_targeted_layer = tk.Entry(convert_window, textvariable=targeted_layer, font=('Verdana', 12), width=30)
    entry_targeted_layer.grid(row=3, column=1)

    label_inferred_layer = tk.Label(convert_window, text="Inferred Layer:", font=('Verdana', 12))
    label_inferred_layer.grid(row=4, column=0)

    entry_inferred_layer = tk.Entry(convert_window, textvariable=inferred_layer, font=('Verdana', 12), width=30)
    entry_inferred_layer.grid(row=4, column=1)

    label_session_description = tk.Label(convert_window, text="Session Description:", font=('Verdana', 12))
    label_session_description.grid(row=5, column=0)

    entry_session_description = tk.Entry(convert_window, textvariable=session_description, font=('Verdana', 12), width=30)
    entry_session_description.grid(row=5, column=1)

    label_lab = tk.Label(convert_window, text="Lab:", font=('Verdana', 12))
    label_lab.grid(row=6, column=0)

    entry_lab = tk.Entry(convert_window, textvariable=lab, font=('Verdana', 12), width=30)
    entry_lab.grid(row=6, column=1)

    label_institution = tk.Label(convert_window, text="Institution:", font=('Verdana', 12))
    label_institution.grid(row=7, column=0)

    entry_institution = tk.Entry(convert_window, textvariable=institution, font=('Verdana', 12), width=30)
    entry_institution.grid(row=7, column=1)

    label_experimenter = tk.Label(convert_window, text="Experimenter:", font=('Verdana', 12))
    label_experimenter.grid(row=8, column=0)

    entry_experimenter = tk.Entry(convert_window, textvariable=experimenter, font=('Verdana', 12), width=30)
    entry_experimenter.grid(row=8, column=1)

    label_subject_id = tk.Label(convert_window, text="Subject ID:", font=('Verdana', 12))
    label_subject_id.grid(row=9, column=0)

    entry_subject_id = tk.Entry(convert_window, textvariable=subject_id, font=('Verdana', 12), width=30)
    entry_subject_id.grid(row=9, column=1)

    label_species = tk.Label(convert_window, text="Species:", font=('Verdana', 12))
    label_species.grid(row=10, column=0)

    entry_species = tk.Entry(convert_window, textvariable=species, font=('Verdana', 12), width=30)
    entry_species.grid(row=10, column=1)

    label_sex = tk.Label(convert_window, text="Sex:", font=('Verdana', 12))
    label_sex.grid(row=11, column=0)

    entry_sex = tk.Entry(convert_window, textvariable=sex, font=('Verdana', 12), width=30)
    entry_sex.grid(row=11, column=1)

    label_date_of_birth = tk.Label(convert_window, text="Date of Birth (YYYY-MM-DD):", font=('Verdana', 12))
    label_date_of_birth.grid(row=12, column=0)

    entry_date_of_birth = tk.Entry(convert_window, textvariable=date_of_birth, font=('Verdana', 12), width=30)
    entry_date_of_birth.grid(row=12, column=1)

    label_nwb_name = tk.Label(convert_window, text="NWB File Name", font=('Verdana', 12))
    label_nwb_name.grid(row=13, column=0)

    entry_nwb_name = tk.Entry(convert_window, textvariable=nwb_name, font=('Verdana', 12), width=30)
    entry_nwb_name.grid(row=13, column=1)

    enter_button = tk.Button(convert_window, text="Enter", width=15, bg="green", fg="black", font=("Verdana", 12), command=on_enter)
    enter_button.grid(row=14, column=0, columnspan=2, pady=10, sticky='s')
    
    convert_window.grab_set()
    convert_window.wait_window()

    return metadata
metadata = {}