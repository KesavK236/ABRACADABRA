import pynwb
from gui_nwb_conversion import nwb_conversion_input_window
import os
import sys
from neuroconv.datainterfaces import AbfInterface
from uuid import uuid4


def convert_to_nwb(file_names, output_folder):
    nofile = "No File Chosen"
    inputs = nwb_conversion_input_window()

    sessions = []
    files_to_convert = []
    if file_names[0] != nofile:
        files_to_convert.append(file_names[0])
        sessions.append( 
            {"abf_file_name": os.path.basename(file_names[0]),
              "stim_type": "long_square",
              "icephys_experiment_type": "current_clamp"}
         )
    if file_names[1] != nofile:
        files_to_convert.append(file_names[1])
        sessions.append( 
            {"abf_file_name": os.path.basename(file_names[1]),
              "stim_type": "long_square",
              "icephys_experiment_type": "current_clamp"}
         )
    if file_names[2] != nofile:
        files_to_convert.append(file_names[2])
        sessions.append( 
            {"abf_file_name": os.path.basename(file_names[2]),
              "stim_type": "long_square",
              "icephys_experiment_type": "current_clamp"}
         )
    if file_names[3] != nofile:
        files_to_convert.append(file_names[3])
        sessions.append( 
            {"abf_file_name": os.path.basename(file_names[3]),
              "stim_type": "ramp",
              "icephys_experiment_type": "current_clamp"}
         )
    if file_names[4] != nofile:
        files_to_convert.append(file_names[4])
        sessions.append( 
            {"abf_file_name": os.path.basename(file_names[4]),
              "stim_type": "ramp",
              "icephys_experiment_type": "current_clamp"}
         )
    if file_names[5] != nofile:
        files_to_convert.append(file_names[5])
        sessions.append( 
            {"abf_file_name": os.path.basename(file_names[5]),
              "stim_type": "short_square",
              "icephys_experiment_type": "current_clamp"}
         )

    icephys_metadata = {
        "cell_id": inputs["cell_id"],
        "slice_id": inputs["slice_id"],
        "targeted_layer": inputs["targeted_layer"],
        "inferred_layer": inputs["inferred_layer"],
        "recording_sessions": sessions
    }

    interface = AbfInterface(
        file_paths=files_to_convert,
        icephys_metadata=icephys_metadata
    )

    sex_string = inputs["sex"]
    if sex_string == "M":
        sex_string = 'M'
    elif sex_string == "F":
        sex_string = 'F'
    elif sex_string == "O":
        sex_string = 'O'
    else:
        sex_string = 'U'

    metadata = interface.get_metadata()
    metadata['NWBFile'].update(
        identifier=str(uuid4()),
        session_description=inputs["session_description"],
        lab=inputs["lab"],
        institution=inputs["institution"],
        experimenter=[inputs["experimenter"]],
    )
    metadata["Subject"] = dict(
        subject_id=inputs["subject_id"],
        species=inputs["species"],
        sex=sex_string,
        date_of_birth= inputs["date_of_birth"]
    )

    folder_name = output_folder + "_outputs"
    output_dir = os.path.join(os.getcwd(), folder_name)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, inputs["NWB_file_name"])
    interface.run_conversion( output_path, metadata=metadata)