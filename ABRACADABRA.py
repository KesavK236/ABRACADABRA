import os
import pyabf
import shutil
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
import pandas as pd
from PIL import ImageTk, Image
from hampel import hampel
from scipy.signal import savgol_filter
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

# from uuid import uuid4
# from neuroconv.datainterfaces import AbfInterface

# pyinstaller -F --icon="ABRACADABRA.ico" --noconsole ABRACADABRA.py
def gui():
    global output_file_entry
    global spinbox_dvdt
    global conversion_bool
    global bool_reset_window
    global check_button_ram
    global check_threshold

    if conversion_bool.get() == 1:
        window.geometry('600x720')
    else:
        window.geometry('600x475')

    clear_frame()

    clear_button_w = 8
    button_enter = tk.Button(window, text="Enter", width=5, height=1, bg="grey", fg="black", command=callback)
    button_file_change1 = tk.Button(window, text="Change File", width=12, height=1, bg="grey", fg="black",
                                    command=file_change1)
    button_file_change2 = tk.Button(window, text="Change File", width=12, height=1, bg="grey", fg="black",
                                    command=file_change2)
    button_file_change3 = tk.Button(window, text="Change File", width=12, height=1, bg="grey", fg="black",
                                    command=file_change3)
    button_file_change4 = tk.Button(window, text="Change File", width=12, height=1, bg="grey", fg="black",
                                    command=file_change4)
    button_file_change5 = tk.Button(window, text="Change File", width=12, height=1, bg="grey", fg="black",
                                    command=file_change5)
    button_file_change6 = tk.Button(window, text="Change File", width=12, height=1, bg="grey", fg="black",
                                    command=file_change6)
    button_file_change7 = tk.Button(window, text="Change File", width=12, height=1, bg="grey", fg="black",
                                    command=file_change7)
    button_file_clear1 = tk.Button(window, text="Clear File", width=clear_button_w, height=1, bg="grey", fg="black",
                                   command=file_clear1)
    button_file_clear2 = tk.Button(window, text="Clear File", width=clear_button_w, height=1, bg="grey", fg="black",
                                   command=file_clear2)
    button_file_clear3 = tk.Button(window, text="Clear File", width=clear_button_w, height=1, bg="grey", fg="black",
                                   command=file_clear3)
    button_file_clear4 = tk.Button(window, text="Clear File", width=clear_button_w, height=1, bg="grey", fg="black",
                                   command=file_clear4)
    button_file_clear5 = tk.Button(window, text="Clear File", width=clear_button_w, height=1, bg="grey", fg="black",
                                   command=file_clear5)
    button_file_clear6 = tk.Button(window, text="Clear File", width=clear_button_w, height=1, bg="grey", fg="black",
                                   command=file_clear6)
    button_file_clear7 = tk.Button(window, text="Clear File", width=clear_button_w, height=1, bg="grey", fg="black",
                                   command=file_clear7)
    spinbox_dvdt = tk.Spinbox(window, from_=1.0, to=100.0, textvariable=spinval, width=5)
    label_spacer = tk.Label(window, text=" ")
    label_spacer2 = tk.Label(window, text=" ")
    label1 = tk.Label(window, text=file_name_presentation(filename1))
    label2 = tk.Label(window, text=file_name_presentation(filename2))
    label3 = tk.Label(window, text=file_name_presentation(filename3))
    label4 = tk.Label(window, text=file_name_presentation(filename4))
    label5 = tk.Label(window, text=file_name_presentation(filename5))
    label6 = tk.Label(window, text=file_name_presentation(filename6))
    label7 = tk.Label(window, text=file_name_presentation(filename7))
    label_rmp = tk.Label(window, text="RMP", font=("Arial", 10))
    label_rheo1s = tk.Label(window, text="Rheo 1s", font=("Arial", 10))
    label_rheo4x = tk.Label(window, text="Rheo 4x", font=("Arial", 10))
    label_ramp1s = tk.Label(window, text="Ramp 1s", font=("Arial", 10))
    label_ramp4x = tk.Label(window, text="Ramp 4x", font=("Arial", 10))
    label_shortrheo_5ms = tk.Label(window, text="Rheo 5ms Single AP", font=("Arial", 10))
    label_shortrheo_1s = tk.Label(window, text="Rheo 1s Single AP", font=("Arial", 10))
    label_dvdt = tk.Label(window, text="Threshold dV/dt in mV/ms", font=("Arial", 10))
    label_title = tk.Label(window, text="ABRACADABRA", font=100)
    label_output_name = tk.Label(window, text="Output File Name:", font=("Arial", 10))
    output_file_entry = tk.Entry(window, textvariable=output_file_name_variable, width=40, justify="center")
    check_check = tk.Checkbutton(window, text='Verify Threshold Value?', command=gui,variable=check_threshold,
	    onvalue=1, offvalue=0)

    # conversion GUI Widgets
    check_conversion = tk.Checkbutton(window, text='Convert to NWB file', command=gui,variable=conversion_bool,
	    onvalue=1, offvalue=0)
    label_conversion = tk.Label(window, text="This Only Queues the Conversion", fg='red', font=("Arial", 12))
    label_cell_id = tk.Label(window, text="Cell ID:", font=("Ariel", 10))
    text_cell_id = tk.Entry(window, textvariable=cell_id, width=30)
    label_slice_id = tk.Label(window, text="Slice ID:", font=("Ariel", 10))
    text_slice_id = tk.Entry(window, textvariable=slice_id, width=30)
    label_target_layer = tk.Label(window, text="Targeted Layer:", font=("Ariel", 10))
    text_target_layer = tk.Entry(window, textvariable=targeted_layer, width=30)
    label_inferred_layer = tk.Label(window, text="Inferred Layer:", font=("Ariel", 10))
    text_inferred_layer = tk.Entry(window, textvariable=inferred_layer, width=30)
    label_session_description = tk.Label(window, text="Session Description", font=("Ariel", 10))
    text_session_description = tk.Entry(window, textvariable=session_description, width=30)
    label_lab = tk.Label(window, text="Lab Name:", font=("Ariel", 10))
    text_lab = tk.Entry(window, textvariable=lab, width=30)
    label_institution = tk.Label(window, text="Institution Name:", font=("Ariel", 10))
    text_institution = tk.Entry(window, textvariable=institution, width=30)
    label_experimenter = tk.Label(window, text="Experimenter Name:", font=("Ariel", 10))
    text_experimenter = tk.Entry(window, textvariable=experimenter, width=30)
    label_subject_id = tk.Label(window, text="Subject ID:", font=("Ariel", 10))
    text_subject_id = tk.Entry(window, textvariable=subject_id, width=30)
    label_species = tk.Label(window, text="Species:", font=("Ariel", 10))
    text_species = tk.Entry(window, textvariable=species, width=30)
    label_sex = tk.Label(window, text="Sex (M, F, U, O):", font=("Ariel", 10))
    text_sex = tk.Entry(window, textvariable=sex, width=30)
    label_date_of_birth = tk.Label(window, text="Date of Birth (YYYY-MM-DD):", font=("Ariel", 10))
    text_date_of_birth = tk.Entry(window, textvariable=date_of_birth, width=30)

    # placement of widgets on the window
    label_title.grid(row=0, column=3, columnspan=2, sticky='W', pady=5)
    label_spacer.grid(row=1, column=0, padx=5)
    label_rmp.grid(row=1, column=2, pady=5, sticky='E')
    label1.grid(row=1, column=4, sticky='W')
    button_file_change1.grid(row=1, column=3)
    button_file_clear1.grid(row=1, padx=25, column=1)
    label_spacer2.grid(row=1, column=5, padx=20)
    label_rheo1s.grid(row=2, column=2, pady=5, sticky='E')
    label2.grid(row=2, column=4, sticky='W')
    button_file_change2.grid(row=2, column=3)
    button_file_clear2.grid(row=2, column=1)
    label_rheo4x.grid(row=3, column=2, pady=5, sticky='E')
    label3.grid(row=3, column=4, sticky='W')
    button_file_change3.grid(row=3, column=3)
    button_file_clear3.grid(row=3, column=1)
    label_ramp1s.grid(row=4, column=2, pady=5, sticky='E')
    label4.grid(row=4, column=4, sticky='W')
    button_file_change4.grid(row=4, column=3)
    button_file_clear4.grid(row=4, column=1)
    label_ramp4x.grid(row=5, column=2, pady=5, sticky='E')
    label5.grid(row=5, column=4, sticky='W')
    button_file_change5.grid(row=5, column=3)
    button_file_clear5.grid(row=5, column=1)
    label_shortrheo_5ms.grid(row=6, column=2, pady=5, sticky='E')
    label6.grid(row=6, column=4, sticky='W')
    button_file_change6.grid(row=6, column=3)
    button_file_clear6.grid(row=6, column=1)
    label_shortrheo_1s.grid(row=7, column=2, pady=5, sticky='E')
    label7.grid(row=7, column=4, sticky='W')
    button_file_change7.grid(row=7, column=3)
    button_file_clear7.grid(row=7, column=1)
    label_dvdt.grid(row=9, column=1, columnspan=2, sticky='E', pady=10)
    spinbox_dvdt.grid(row=9, column=3)
    check_conversion.grid(row=11, column=3)
    check_check.grid(row=10, column=3)
    label_output_name.grid(row=25, column=3)
    output_file_entry.grid(row=26, column=2, columnspan=4, sticky='W', padx= 70)
    button_enter.grid(row=27, column=3, pady=5)   

    if conversion_bool.get() == 1:
        label_cell_id.grid(row=12, column=0, columnspan=3, sticky='E')
        text_cell_id.grid(row=12, column=3, columnspan=4, sticky='W')
        label_slice_id.grid(row=13, column=0, columnspan=3, sticky='E')
        text_slice_id.grid(row=13, column=3, columnspan=4, sticky='W')
        label_target_layer.grid(row=14, column=0, columnspan=3, sticky='E')
        text_target_layer.grid(row=14, column=3, columnspan=4, sticky='W')
        label_inferred_layer.grid(row=15, column=0, columnspan=3, sticky='E')
        text_inferred_layer.grid(row=15, column=3, columnspan=4, sticky='W')
        label_session_description.grid(row=16, column=0, columnspan=3, sticky='E')
        text_session_description.grid(row=16, column=3, columnspan=4, sticky='W')
        label_lab.grid(row=17, column=0, columnspan=3, sticky='E')
        text_lab.grid(row=17, column=3, columnspan=4, sticky='W')
        label_institution.grid(row=18, column=0, columnspan=3, sticky='E')
        text_institution.grid(row=18, column=3, columnspan=4, sticky='W')
        label_experimenter.grid(row=19, column=0, columnspan=3, sticky='E')
        text_experimenter.grid(row=19, column=3, columnspan=4, sticky='W')
        label_subject_id.grid(row=20, column=0, columnspan=3, sticky='E')
        text_subject_id.grid(row=20, column=3, columnspan=4, sticky='W')
        label_species.grid(row=21, column=0, columnspan=3, sticky='E')
        text_species.grid(row=21, column=3, columnspan=4, sticky='W')
        label_sex.grid(row=22, column=0, columnspan=3, sticky='E')
        text_sex.grid(row=22, column=3, columnspan=4, sticky='W')
        label_date_of_birth.grid(row=23, column=0, columnspan=3, sticky='E')
        text_date_of_birth.grid(row=23, column=3, columnspan=4, sticky='W')
        label_conversion.grid(row=24, column=2, columnspan=4, padx=30)
    else:
        label_spacer.grid(row=12, column=0, pady=10)
   
    if check_button_ram != conversion_bool.get():
        check_button_ram = conversion_bool.get()
        bool_reset_window = True
    if bool_reset_window == True:
        bool_reset_window = False
        return
    else:
        window.protocol("WM_DELETE_WINDOW", on_closing)
        window.mainloop()
        print("continuing")


def on_closing():
    window.destroy()

def file_name_presentation(file_name):
    j = len(file_name) - 1
    if j == -1 :
        return "No File Chosen"
    else:
        while file_name[j] != "/" and j > -1:
            j -= 1
        return file_name[j + 1:len(file_name)]


def file_change1():
    global abf
    global filename1
    global bool_reset_window
    filename1 = askopenfilename()
    if filename1 == '':
        filename1 = "No File Chosen"
    bool_reset_window = True
    gui()


def file_change2():
    global abf
    global filename2
    global bool_reset_window
    filename2 = askopenfilename()
    if filename2 == '':
        filename2 = "No File Chosen"
    bool_reset_window = True
    gui()


def file_change3():
    global abf
    global filename3
    global bool_reset_window
    filename3 = askopenfilename()
    if filename3 == '':
        filename3 = "No File Chosen"
    bool_reset_window = True
    gui()


def file_change4():
    global abf
    global filename4
    global bool_reset_window
    filename4 = askopenfilename()
    if filename4 == '':
        filename4 = "No File Chosen"
    bool_reset_window = True
    gui()


def file_change5():
    global abf
    global filename5
    global bool_reset_window
    filename5 = askopenfilename()
    if filename5 == '':
        filename5 = "No File Chosen"
    bool_reset_window = True
    gui()


def file_change6():
    global abf
    global filename6
    global bool_reset_window
    filename6 = askopenfilename()
    if filename6 == '':
        filename6 = "No File Chosen"
    bool_reset_window = True
    gui()


def file_change7():
    global abf
    global filename7
    global bool_reset_window
    filename7 = askopenfilename()
    if filename7 == '':
        filename7 = "No File Chosen"
    bool_reset_window = True
    gui()


def file_clear1():
    global abf
    global filename1
    global bool_reset_window
    filename1 = "No File Chosen"
    bool_reset_window = True
    gui()


def file_clear2():
    global abf
    global filename2
    global bool_reset_window
    filename2 = "No File Chosen"
    bool_reset_window = True
    gui()


def file_clear3():
    global abf
    global filename3
    global bool_reset_window
    filename3 = "No File Chosen"
    bool_reset_window = True
    gui()


def file_clear4():
    global abf
    global filename4
    global bool_reset_window
    filename4 = "No File Chosen"
    bool_reset_window = True
    gui()


def file_clear5():
    global abf
    global filename5
    global bool_reset_window
    filename5 = "No File Chosen"
    bool_reset_window = True
    gui()


def file_clear6():
    global abf
    global filename6
    global bool_reset_window
    filename6 = "No File Chosen"
    bool_reset_window = True
    gui()


def file_clear7():
    global abf
    global filename7
    global bool_reset_window
    filename7 = "No File Chosen"
    bool_reset_window = True
    gui()


def clear_frame():
    for widgets in window.winfo_children():
        widgets.destroy()
    return


def num_sweeps():
    global abf
    num_sweep = 0
    sweep_bool = 1
    while sweep_bool:
        try:
            abf.setSweep(num_sweep)
            num_sweep += 1
        except ValueError:
            sweep_bool = 0
    return num_sweep


def current_injection_start(sweep_c):
    curr_start_index = 0
    while sweep_c[curr_start_index] == 0:
        curr_start_index += 1
        if curr_start_index >= len(sweep_c):
            curr_start_index = 1
            break
    curr_start_index -= 1
    return curr_start_index


def ap_curr_and_time(sweep_x, sweep_y, sweep_c, sweep_y_d, sweep_x_d, curr_start_index):
    global spinbox_dvdt
    return_array = [0, 0, 0, 0]
    j = curr_start_index
    resting_current = sweep_c[j-10]
    ap_bool = 0
    threshold_dvdt = int(spinbox_dvdt.get())
    # maybe need to add a extra check to ensure this is an action potential
    while j < len(sweep_c) - 1 and ap_bool == 0:
        if sweep_y_d[j] > threshold_dvdt:
            ap_bool = 1
            return_array[0] = 1
            return_array[1] = sweep_c[j]
            return_array[2] = sweep_c[j] - resting_current
            return_array[3] = sweep_x_d[j] - sweep_x[curr_start_index]

        j += 1
    return return_array


def check_no_change(sweep_y_d, j, increasing):
    for i in range(10):
        if sweep_y_d[j + i] > 0 and increasing:
            return 0
        elif sweep_y_d[j + i] < 0 and not increasing:
            return 0
    return 1


def two_sig_figs(num):
    count = 0
    while abs(num) < 10:
        num = num * 10
        count += 1
    round_check = int(num * 10) % 10
    if round_check > 5:
        num += 1
    count = count - 3
    num = int(num) / (10 ** count)
    return num


def no_spaces(name):
    for i in range(0, len(name)):
        if name[i] == ' ':
            name = name.replace(' ', '_')
    return name

def threshold_window(sweep_x, sweep_y, threshold_time, threshold_volt, protocol):
    global thresh_window
    global keep_window_open
    global window_check_bool 
    global window_upper_limit_entry
    global window_lower_limit_entry
    keep_window_open = 1
    thresh_window = tk.Tk()
    thresh_window.title("Threshold Check")
    thresh_window.geometry("600x200")   
    current_directory = os.getcwd()
    try:
        thresh_window.iconbitmap(current_directory + "\\ABRACADABRA.ico")
    except:
        print("Icon not in correct directory, but not necessary")
    plt.clf()
    ax1 = plt.subplot()
    ax1.set_ylabel(abf.sweepLabelY)
    ax1.set_xlabel(abf.sweepLabelX)
    ax1.plot(sweep_x, sweep_y, alpha=.5)
    ax1.plot(threshold_time, threshold_volt, marker="o", markersize=2, markeredgecolor="green", markerfacecolor="green")
    plt.grid()
    image_name = protocol + " Short Rheo Trace with Estimated Threshold.jpg"
    plt.title(image_name[:-4])

    plt.show(block=False)

    button_thresh_good = tk.Button(thresh_window, text="Threshold is good!", width=20, height=1, bg="grey", fg="black",
                                    command=thresh_good_button)
    button_thresh_window = tk.Button(thresh_window, text="Search in this window", width=20, height=1, bg="grey", fg="black",
                                    command=window_button)
    button_sweep_increase = tk.Button(thresh_window, text="Check next sweep", width=20, height=1, bg="grey", fg="black",
                                    command=sweep_increase)
    window_upper_limit_label = tk.Label(thresh_window, text="Upper Time Limit (sec):")
    window_upper_limit_entry = tk.Entry(thresh_window, width=5)
    window_lower_limit_label = tk.Label(thresh_window, text="Lower Time Limit (sec):")
    window_lower_limit_entry = tk.Entry(thresh_window, width=5)
    button_thresh_good.grid(column=0, row=4, padx=15, pady=15)
    button_thresh_window.grid(column=1, row=4, padx=15, pady=15, columnspan=2)
    button_sweep_increase.grid(column=3, row=4, padx=15, pady=15)
    thresh_question_label = tk.Label(thresh_window, text="Does the chosen threshold look correct?")
    thresh_question_label.grid(column=0, row=1, columnspan=3, pady=15)
    window_upper_limit_label.grid(column=1, row=2, sticky="E")
    window_upper_limit_entry.grid(column=2, row=2, sticky="W")    
    window_lower_limit_label.grid(column=1, row=3, sticky="E")
    window_lower_limit_entry.grid(column=2, row=3, sticky="W")
    while keep_window_open:
        thresh_window.update_idletasks()
        thresh_window.update()
    thresh_window.destroy()
    plt.close()
    return


def thresh_good_button():
    global window_check_bool
    global keep_window_open
    window_check_bool = 1
    keep_window_open = 0

def window_button():
    global upper_window
    global lower_window
    global use_window
    global window_upper_limit_entry
    global window_lower_limit_entry
    global window_check_bool
    global keep_window_open
    use_window = 1
    upper_window = float(window_upper_limit_entry.get())
    lower_window = float(window_lower_limit_entry.get())
    keep_window_open = 0
    window_check_bool = 0


def sweep_increase():
    global window_check_bool
    global keep_window_open
    global sweep_ram
    window_check_bool = 0
    keep_window_open = 0
    sweep_ram += 1


def rmp(file_name, f):
    global abf
    if file_name == "No File Chosen":
        return
    print("Rmp Data:")
    f.write("Rmp Data:")
    f.write('\n')
    resting_potential = 0
    abf = pyabf.ABF(file_name)
    abf.setSweep(0)
    sweep_x = np.array(abf.sweepX)
    sweep_y = savgol_filter(np.array(abf.sweepY), window_length=25, polyorder=3)
    sum_potentials = 0
    for i in range(len(sweep_x)):
        sum_potentials += sweep_y[i]
    resting_potential = sum_potentials / len(sweep_x)

    print("Resting Membrane Potential (mV): " + str(resting_potential))
    f.write("Resting Membrane Potential (mV):, " + str(resting_potential))
    f.write('\n')

    plt.clf()
    ax1 = plt.subplot()
    ax1.set_ylabel(abf.sweepLabelY)
    ax1.set_xlabel(abf.sweepLabelX)
    ax1.plot(sweep_x, sweep_y, alpha=.5)
    plt.grid()
    image_name = no_spaces(output_file_entry.get()) + "_rmp_graph.png"
    plt.title(image_name[:-4])
    image_path = os.path.join(final_directory, image_name)
    plt.savefig(image_path)


def rheo_1s(file_name, f):
    global abf
    if file_name == "No File Chosen":
        return
    print("Rheo_1s Data:")
    f.write("Rheo_1s Data:")
    f.write('\n')
    abf = pyabf.ABF(file_name)
    num_sweep = num_sweeps()
    hyper_pol_input_res = 0
    hyper_pol_count = 0
    average_sag = 0
    ap_bool = 0
    current_threshold = 0
    rheobase = 0
    ap_delay = 0
    image_made_bool = 0

    for i in range(num_sweep):
        abf.setSweep(i)
        sweep_x = np.array(abf.sweepX)
        sweep_y = savgol_filter(np.array(abf.sweepY), window_length=25, polyorder=3)
        sweep_c = np.array(abf.sweepC)

        # calculate derivative of sweep_y
        sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
        sweep_x_d = sweep_x[1:len(sweep_x)]

        # get time of current injection
        curr_start_index = current_injection_start(sweep_c)

        # get time of current injection conclusion
        curr_end_index = curr_start_index + 1
        while sweep_c[curr_end_index] != 0:
            curr_end_index += 1
            if curr_end_index >= len(sweep_c):
                break
        curr_end_index -= 1

        # analyze hyperpolarized currents
        if sweep_c[curr_start_index + 1] < 0:
            v_min = np.min(sweep_y)

            # baseline voltage
            count = 0
            sum_voltage = 0
            for j in range(200, 400, 1):
                sum_voltage += sweep_y[j]
                count += 1
            base_volt = sum_voltage / count

            # end current volt and curr
            count_end_voltage = 0
            sum_end_voltage = 0
            count_end_current = 0
            sum_end_current = 0
            for k in range(curr_end_index - 200, curr_end_index, 1):
                sum_end_voltage += sweep_y[k]
                count_end_voltage += 1
                sum_end_current += sweep_c[k]
                count_end_current += 1
            end_curr = sum_end_current / count_end_current
            end_volt = sum_end_voltage / count_end_voltage

             # input resistance
            if hyper_pol_count < 1:
                average_sag = v_min / end_volt

            hyper_pol_input_res += (((end_volt - base_volt) * (10 ** -3)) / (end_curr * (10 ** -9)))
            hyper_pol_count += 1

        ap_max = max(sweep_y)
        if sweep_c[curr_start_index + 1] > 0 and ap_bool == 0 and ap_max > 0:
            return_array = ap_curr_and_time(sweep_x, sweep_y, sweep_c, sweep_y_d, sweep_x_d, curr_start_index)
            ap_bool = return_array[0]
            current_threshold = return_array[1]
            rheobase = return_array[2]
            ap_delay = return_array[3]

        if ap_bool == 1 and image_made_bool == 0:
            plt.clf()
            plt.grid()
            ax1 = plt.subplot()
            ax1.set_ylabel(abf.sweepLabelY)
            ax1.set_xlabel(abf.sweepLabelX)
            ax1.plot(sweep_x, sweep_y, alpha=.5)
            image_name = no_spaces(output_file_entry.get()) + "_rheo_1s_graph.png"
            plt.title(image_name[:-4])
            image_path = os.path.join(final_directory, image_name)
            plt.savefig(image_path)
            image_made_bool = 1

    if hyper_pol_count > 0:
        input_res = hyper_pol_input_res / ((10 ** 6)* hyper_pol_count)
        omega = chr(0x3a9)
        print("Average Input Resistance (M" + omega + "): " + str(input_res))
        f.write("Average Input Resistance (Mega Ohms):, " + str(input_res))
        f.write('\n')
        print("Voltage Sag: " + str(average_sag))
        f.write("Voltage Sag:, " + str(average_sag))
        f.write('\n')

    if ap_bool == 1:
        # print("Current at Threshold (nA): " + str(current_threshold))
        # f.write("Current at Threshold (nA):, " + str(current_threshold))
        # f.write('\n')
        print("Rheobase (nA): " + str(rheobase))
        f.write("Rheobase (nA):, " + str(rheobase))
        f.write('\n')
        ap_delay = two_sig_figs(ap_delay)
        print("Time to Spike (ms): " + str(ap_delay))
        f.write("Time to Spike (ms):, " + str(ap_delay))
        f.write('\n')


def rheo_4x(file_name, f):
    global abf
    global spinbox_dvdt
    threshold_dvdt = int(spinbox_dvdt.get())
    if file_name == "No File Chosen":
        return
    print("Rheo_4x Data:")
    f.write("Rheo_4x Data:")
    f.write('\n')
    abf = pyabf.ABF(file_name)

    for i in range(4):
        abf.setSweep(i)
        sweep_x = np.array(abf.sweepX)
        sweep_y = savgol_filter(np.array(abf.sweepY), window_length=25, polyorder=3)
        sweep_c = np.array(abf.sweepC)

        sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
        sweep_x_d = sweep_x[1:len(sweep_x)]

        curr_start_index = current_injection_start(sweep_c)

        j = curr_start_index + 30
        ap_found = 0
        finding_peak = 0
        ap_count = 0
        threshold_ram = 0

        
        plt.clf()
        plt.grid()
        ax1 = plt.subplot()
        ax1.set_ylabel(abf.sweepLabelY)
        ax1.set_xlabel(abf.sweepLabelX)
        ax1.plot(sweep_x, sweep_y, alpha=.5, label=" sweep %d voltage" % i)
        image_name = no_spaces(output_file_entry.get()) + "_rheo_" + str(i+1) + "x_graph.png"
        plt.title(image_name[:-4])
        image_path = os.path.join(final_directory, image_name)
        plt.savefig(image_path)

        while j < len(sweep_y_d) - 1:
            if sweep_y_d[j] >= threshold_dvdt and ap_found == 0 and finding_peak == 0:

                ap_found = 1
                finding_peak = 1
                threshold_ram = sweep_y[j]
                # ax1.plot(sweep_x[j], sweep_y[j], marker="o", markersize="10", markeredgecolor="blue",
                #          markerfacecolor="blue")

            elif finding_peak == 1 and sweep_y_d[j] < 0 < sweep_y[j] and sweep_y[j] - threshold_ram > 20:
                if check_no_change(sweep_y_d, j, 1):
                    finding_peak = 0
                    ap_count += 1
                    # ax1.plot(sweep_x[j], sweep_y[j], marker="o", markersize="10", markeredgecolor="green",
                    #          markerfacecolor="green")

            elif finding_peak == 0 and ap_found == 1 and sweep_y_d[j] > 0:
                if check_no_change(sweep_y_d, j, 0):
                    ap_found = 0
                    # ax1.plot(sweep_x[j], sweep_y[j], marker="o", markersize="10", markeredgecolor="red",
                    #          markerfacecolor="red")
            j += 1
        # plt.show()
        print("Number of Action Potentials in Rheo " + str(i + 1) + "x rheobase:" + str(ap_count))
        f.write("Number of Action Potentials in Rheo " + str(i + 1) + "x rheobase:, " + str(ap_count))
        f.write('\n')


def ramp_1s(file_name, f):
    global abf

    if file_name == "No File Chosen":
        return
    print("Ramp_1s Data:")
    f.write("Ramp_1s Data:")
    f.write('\n')
    abf = pyabf.ABF(file_name)
    num_sweep = num_sweeps()
    ap_bool = 0
    threshold_curr = 0
    ap_delay = 0
    curr_delta = 0
    image_made_bool = 0

    for i in range(num_sweep):
        abf.setSweep(i)
        sweep_x = np.array(abf.sweepX)
        sweep_y = savgol_filter(np.array(abf.sweepY), window_length=25, polyorder=3)
        sweep_c = np.array(abf.sweepC)

        sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
        sweep_x_d = sweep_x[1:len(sweep_x)]

        # get time of current injection
        curr_start_index = current_injection_start(sweep_c)

        ap_max = max(sweep_y)
        if sweep_c[curr_start_index + 1] > 0 and ap_bool == 0 and ap_max > 0:
            return_array = ap_curr_and_time(sweep_x, sweep_y, sweep_c, sweep_y_d, sweep_x_d, curr_start_index)
            ap_bool = return_array[0]
            threshold_curr = return_array[1]
            curr_delta = return_array[2]
            ap_delay = return_array[3]

        if ap_bool == 1 and image_made_bool == 0:
            plt.clf()
            plt.grid()
            ax1 = plt.subplot()
            ax1.set_ylabel(abf.sweepLabelY)
            ax1.set_xlabel(abf.sweepLabelX)
            ax1.plot(sweep_x, sweep_y, alpha=.5)
            image_name = no_spaces(output_file_entry.get()) + "_ramp_1s_graph.png"
            plt.title(image_name[:-4])    
            image_path = os.path.join(final_directory, image_name)
            plt.savefig(image_path)
            image_made_bool = 1
    if ap_bool == 1:
        # print("Current at Threshold (nA): " + str(threshold_curr))
        # f.write("Current at Threshold (nA):, " + str(threshold_curr))
        # f.write('\n')
        print("Rheobase (nA): " + str(curr_delta))
        f.write("Rheobase(nA):, " + str(curr_delta))
        f.write('\n')
        ap_delay = two_sig_figs(ap_delay)
        print("Time to Spike (ms): " + str(ap_delay))
        f.write("Time to Spike (ms):, " + str(ap_delay))
        f.write('\n')


def ramp_4x(file_name, f):
    global abf
    global spinbox_dvdt
    threshold_dvdt = int(spinbox_dvdt.get())
    if file_name == "No File Chosen":
        return
    print("Ramp_4x Data:")
    f.write("Ramp_4x Data:")
    f.write('\n')
    abf = pyabf.ABF(file_name)

    for i in range(4):
        abf.setSweep(i)
        sweep_x = np.array(abf.sweepX)
        sweep_y = savgol_filter(np.array(abf.sweepY), window_length=25, polyorder=3)
        sweep_c = np.array(abf.sweepC)
        sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
        curr_start_index = current_injection_start(sweep_c)

        j = curr_start_index + 30
        ap_found = 0
        finding_first = 0
        finding_peak = 0
        ap_count = 0

        # find current end
        current_end = j
        while sweep_c[current_end] > 0:
            current_end += 1
        current_end = current_end - 2
        # Graphing to Debug
        # plt.clf()
        # ax1 = plt.subplot()
        # ax2 = ax1.twinx()
        # ax1.set_ylabel(abf.sweepLabelY)
        # ax1.set_xlabel(abf.sweepLabelX)
        # ax2.set_ylabel(abf.sweepLabelC)
        #
        # ax1.plot(sweep_x, sweep_y, alpha=.5, label=" sweep %d voltage" % i)
        # # ax1.plot(xhat, yhat, alpha=.5, label=" sweep %d voltage" % i)
        # ax2.plot(sweep_x, sweep_c, alpha=.5, label="sweep %d current" % i, color='green')
        #
        # plt.legend()
        plt.clf()
        plt.grid()
        ax1 = plt.subplot()
        ax1.set_ylabel(abf.sweepLabelY)
        ax1.set_xlabel(abf.sweepLabelX)
        ax1.plot(sweep_x, sweep_y, alpha=.5, label=" sweep %d voltage" % i)
        image_name = no_spaces(output_file_entry.get()) + "_ramp_" + str(i+1) + "x_graph.png"
        plt.title(image_name[:-4])
        image_path = os.path.join(final_directory, image_name)
        plt.savefig(image_path)

        # AP Counting Block
        while j < current_end:
            # Find Threshold point of the first ap
            if sweep_y_d[j] >= threshold_dvdt and ap_found == 0 and finding_peak == 0 and finding_first:
                finding_first = 0
                ap_found = 1
                finding_peak = 1

            # Find the threshold point of subsequent APs
            elif sweep_y_d[j] >= 0 and ap_found == 0 and finding_peak == 0 and finding_first == 0:
                ap_found = 1
                finding_peak = 1

            # Find the peak of current AP
            elif finding_peak == 1 and sweep_y_d[j] < 0 < sweep_y[j]:
                if check_no_change(sweep_y_d, j, 1):
                    finding_peak = 0
                    ap_count += 1      

            # Find the end of the downstroke of current AP
            elif finding_peak == 0 and ap_found == 1 and sweep_y_d[j] > 0:
                if check_no_change(sweep_y_d, j, 0):
                    ap_found = 0
            j += 1
        # plt.show()
        print("Number of Action Potentials in Ramp " + str(i + 1) + "x threshold: " + str(ap_count))
        f.write("Number of Action Potentials in Ramp " + str(i + 1) + "x threshold:, " + str(ap_count))
        f.write('\n')


def short_rheo_5ms(file_name, f):
    global abf
    global spinbox_dvdt
    global window_check_bool
    global lower_window
    global upper_window
    global use_window
    global sweep_ram
    global check_threshold
    if file_name == "No File Chosen":
        return
    print("Rheo_5ms Data:")
    f.write("Rheo_5ms Data:")
    f.write('\n')
    abf = pyabf.ABF(file_name)
    total_sweeps = num_sweeps()
    sweep_number = -1
    ap_max = -1
    dv_peak = 0
    # Find the AP sweep
    while ap_max < 0 or dv_peak < 20:
        sweep_number += 1
        sweep_ram = sweep_number
        if sweep_number >= total_sweeps:
            print("Conditions for AP were not met, consider changing the dvdt")
            return
        abf.setSweep(sweep_number)
        sweep_x = np.array(abf.sweepX)
        sweep_y = np.array(abf.sweepY)
        sweep_y = savgol_filter(np.array(abf.sweepY), window_length=25, polyorder=3)
        sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
        sweep_c = np.array(abf.sweepC)
        ap_max = max(sweep_y)
        k = 0
        curr_start_index = current_injection_start(sweep_c)
        curr_end_index = len(sweep_c) - 100

        current_window_dvdt = sweep_y_d[curr_start_index + 100:curr_end_index]

        dv_peak = max(current_window_dvdt)

    window_check_bool = 0
    while  window_check_bool == 0:  
        sweep_number = sweep_ram
        abf.setSweep(sweep_number)
        print("sweep number = " + str(sweep_number))

        sweep_x = np.array(abf.sweepX)
        sweep_y = np.array(abf.sweepY)
        sweep_y = savgol_filter(np.array(abf.sweepY), window_length=25, polyorder=3)
        sweep_y_raw = np.array(abf.sweepY)
        sweep_c = np.array(abf.sweepC)

        sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
        
        sweep_x_d = sweep_x[1:]
        sweep_y_1 = sweep_y[1:]

        # filter dvdt for calcuation purposes
        sweep_y_d_filtered = hampel(sweep_y_d, window_size=3, n_sigma=3.0).filtered_data

        # get time of current injection initiation
        curr_start_index = current_injection_start(sweep_c)
        threshold_curr = sweep_c[curr_start_index + 5]

        # get holding current
        count = 0
        sum_curr = 0
        for j in range(curr_start_index - 101, curr_start_index - 1):
            sum_curr += sweep_c[j]
            count += 1
        holding_curr = sum_curr / count


        # get time of current injection conclusion
        curr_end_index = len(sweep_c) - 100


        # Get steady state current at the end of the trace
        count = 0
        sum_voltage = 0
        for j in range(curr_end_index - 200, curr_end_index):
            sum_voltage += sweep_y[j]
            count += 1
        steady_state_volt = sum_voltage / count

        # Get peak volt, index and time
        peak_volt = max(sweep_y)
        peak_index = np.argmax(sweep_y)
        peak_time = sweep_x[peak_index]

        dvdt_threshold = int(spinbox_dvdt.get())

        # # # Get threshold by going backwards from voltage peak
        # k = peak_index
        # while sweep_y_d[k] < dvdt_threshold:
        #     k -= 1
        # while sweep_y_d[k] > dvdt_threshold:
        #     k-= 1
        # threshold_index = k
        # threshold_volt = sweep_y[threshold_index]
        # threshold_time = sweep_x[threshold_index]
        
        # get threshold thorugh convoluted method but technically more accurate to physiology
        k = current_injection_start(sweep_c) + 30
        sweep_y_d_2 = np.diff(sweep_y_d) / (1000 * np.diff(sweep_x_d))

        if use_window == 1:
            k = 0
            while sweep_x[k] < lower_window:
                k += 1
            
            while (sweep_y_d_filtered[k] < dvdt_threshold or sweep_y_d_2[k] < 0) and sweep_x[k] < upper_window:
                k += 1
                threshold_index = k
                threshold_volt = sweep_y[threshold_index]
                threshold_time = sweep_x[threshold_index]  
                
        else:
            while sweep_y_d_filtered[k] < dvdt_threshold or sweep_y_d_2[k] < 0:
                k += 1
            threshold_index = k
            threshold_volt = sweep_y[threshold_index]
            threshold_time = sweep_x[threshold_index]

        if check_threshold.get() == 1:
            threshold_window(sweep_x, sweep_y, threshold_time, threshold_volt, "5ms")
        
        else:
            window_check_bool = 1
    
    window_check_bool = 0
    use_window = 0
    
    # Find the deltas for rising phase
    halfwidth_volt = (peak_volt + threshold_volt) / 2
    rise_delta = peak_volt - threshold_volt
    rise_volt_10 = (rise_delta * .1) + threshold_volt
    rise_volt_90 = (rise_delta * .9) + threshold_volt
    fall_volt_10 = rise_volt_90
    fall_volt_90 = rise_volt_10
    
    # find the time points of rising phase
    k = threshold_index
    while sweep_y[k] < rise_volt_10:
        k += 1
    rise_time_10 = sweep_x[k]

    while sweep_y[k] < halfwidth_volt:
        k += 1
    halfwidth_start = sweep_x[k]

    while sweep_y[k] < rise_volt_90:
        k += 1
    rise_time_90 = sweep_x[k]

    # find time points of falling phase
    k = peak_index
    while sweep_y[k] > fall_volt_10:
        k += 1
    fall_time_10 = sweep_x[k]

    while sweep_y[k] > halfwidth_volt:
        k += 1
    halfwidth_end = sweep_x[k]

    while sweep_y[k] > fall_volt_90:
        k += 1
    fall_time_90 = sweep_x[k]

    while sweep_y[k] > threshold_volt:
        k += 1
    end_fall = sweep_x[k]
    end_fall_index = k
    
    # determine ahp points
    l = k
    # find the nearest steady state point
    while sweep_y_d_filtered[l] < 0:
        l += 1
    while sweep_y[l] > steady_state_volt:
        l += 1
    ap_end_index = l

    ahp = 0
    ahp_index = 0
    ahp_array = sweep_y[end_fall_index:ap_end_index]
    ahp = min(ahp_array)
    ahp_index = np.argmin(ahp_array)
    
    ahp_halfwidth_volt = (steady_state_volt + ahp) / 2

    # find ahp time points
    k = end_fall_index
    while sweep_y[k] > ahp_halfwidth_volt:
        k +=1
    ahp_halfwidth_start = sweep_x[k]

    k = ahp_index
    while sweep_y[k] < ahp_halfwidth_volt:
        k += 1
    ahp_halfwidth_end = sweep_x[k]

    rise_time_raw = peak_time - threshold_time
    rise_time_10_90 = rise_time_90 - rise_time_10
    fall_time_raw = end_fall - peak_time
    fall_time_10_90 = fall_time_90 - fall_time_10
    halfwidth = halfwidth_end - halfwidth_start
    ahp_halfwidth = ahp_halfwidth_start - ahp_halfwidth_end
    rheobase = threshold_curr - holding_curr

    print("Relative Rheobase (nA): " + str(rheobase))
    f.write("Relative Rheobase (nA):, " + str(rheobase))
    f.write('\n')
    print("AP Peak (mV): " + str(peak_volt))
    f.write("AP Peak (mV):, " + str(peak_volt))
    f.write('\n')
    print("AP Amplitude (mV): " + str(peak_volt-threshold_volt))
    f.write("AP Amplitude (mV):, " + str(peak_volt-threshold_volt))
    f.write('\n')
    print("AP Voltage Threshold (mV): " + str(threshold_volt))
    f.write("AP Voltage Threshold (mV):, " + str(threshold_volt))
    f.write('\n')
    rise_time_raw = two_sig_figs(rise_time_raw)
    rise_time_10_90 = two_sig_figs(rise_time_10_90)
    print("AP Rise Time Raw (ms): " + str(rise_time_raw))
    f.write("AP Rise Time Raw (ms):, " + str(rise_time_raw))
    f.write('\n')
    print("AP Rise Time 10-90 (ms): " + str(rise_time_10_90))
    f.write("AP Rise Time 10-90 (ms):, " + str(rise_time_10_90))
    f.write('\n')
    halfwidth = two_sig_figs(halfwidth)
    print("AP Halfwidth (ms): " + str(halfwidth))
    f.write("AP Halfwidth (ms):, " + str(halfwidth))
    f.write('\n')
    fall_time_raw = two_sig_figs(fall_time_raw)
    fall_time_10_90 = two_sig_figs(fall_time_10_90)
    print("AP Falling Time Raw (ms): " + str(fall_time_raw))
    f.write("AP Falling Time Raw (ms):, " + str(fall_time_raw))
    f.write('\n')
    print("AP Falling Time 10-90 (ms): " + str(fall_time_10_90))
    f.write("AP Falling Time 10-90 (ms):, " + str(fall_time_10_90))
    f.write('\n')
    print("AHP Minimum (mV): " + str(ahp))
    f.write("AHP Minimum (mV):, " + str(ahp))
    f.write('\n')
    print("AHP Relative (mV): " + str(ahp - threshold_volt))
    f.write("AHP Relative (mV):, " + str(ahp - threshold_volt))
    f.write('\n')
    ahp_halfwidth = two_sig_figs(ahp_halfwidth)
    print("AHP half-width (ms): " + str(ahp_halfwidth))
    f.write("AHP half-width (ms):, " + str(ahp_halfwidth))
    f.write('\n')
    print("Upstroke-Downstroke ratio: " + str(rise_time_10_90 / fall_time_10_90))
    f.write("Upstroke-Downstroke ratio:, " + str(rise_time_10_90 / fall_time_10_90))
    f.write('\n')

    phase_plane(sweep_x_d, sweep_y_1, sweep_y_d, "5ms")

    # Graphing single AP
    plt.clf()
    plt.grid()
    ax1 = plt.subplot()
    # ax2 = ax1.twinx()
    ax1.set_ylabel(abf.sweepLabelY)
    ax1.set_xlabel(abf.sweepLabelX)
    # ax2.set_ylabel(abf.sweepLabelC)
    ax1.plot(sweep_x, sweep_y, alpha=.5, label=" sweep %d voltage" % sweep_number)
    image_name = no_spaces(output_file_entry.get()) + "_rheo_5ms_single_ap_graph.png"
    plt.title(image_name[:-4])
    image_path = os.path.join(final_directory, image_name)
    plt.savefig(image_path)

def short_rheo_1s(file_name, f):
    global abf
    global spinbox_dvdt
    global window_check_bool
    global lower_window
    global upper_window
    global use_window
    global sweep_ram
    global check_threshold
    if file_name == "No File Chosen":
        return
    print("Rheo_1s Data:")
    f.write("Rheo_1s Data:")
    f.write('\n')
    abf = pyabf.ABF(file_name)
    total_sweeps = num_sweeps()
    sweep_number = -1
    ap_max = -1
    dv_peak = 0
    while ap_max < 0 or dv_peak < 20:
        sweep_number += 1
        if sweep_number >= total_sweeps:
            print("Conditions for AP were not met, consider changing the dvdt")
            return
        abf.setSweep(sweep_number)
        sweep_x = np.array(abf.sweepX)
        sweep_y = np.array(abf.sweepY)
        sweep_y = savgol_filter(np.array(abf.sweepY), window_length=25, polyorder=3)
        sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
        sweep_c = np.array(abf.sweepC)
        ap_max = max(sweep_y)
        k = 0
        curr_start_index = current_injection_start(sweep_c)
        curr_end_index = curr_start_index + 1
        if curr_start_index != 0:
            while sweep_c[curr_end_index] != 0:
                curr_end_index += 1
            curr_end_index -= 1

            current_window_dvdt = sweep_y_d[curr_start_index + 100:curr_end_index]

            dv_peak = max(current_window_dvdt)
        else:
            dv_peak = 0
    sweep_ram = sweep_number    
    print("sweep number = " + str(sweep_number))

    window_check_bool = 0
    while window_check_bool == 0:
        sweep_number = sweep_ram
        print(sweep_number)
        abf.setSweep(sweep_number)
        sweep_x = np.array(abf.sweepX)
        sweep_y = np.array(abf.sweepY)
        sweep_y = savgol_filter(np.array(abf.sweepY), window_length=25, polyorder=3)
        sweep_y_raw = np.array(abf.sweepY)
        sweep_c = np.array(abf.sweepC)

        sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
        sweep_x_d = sweep_x[1:]
        sweep_y_1 = sweep_y[1:]

        # filter the dvdt graph for easier calculations
        sweep_y_d_filtered = hampel(sweep_y_d, window_size=3, n_sigma=3.0).filtered_data

        # get time of current injection initiation
        curr_start_index = current_injection_start(sweep_c)
        threshold_curr = sweep_c[curr_start_index + 5]


        # get holding current
        count = 0
        sum_curr = 0
        for j in range(curr_start_index - 101, curr_start_index - 1):
            sum_curr += sweep_c[j]
            count += 1
        holding_curr = sum_curr / count


        # get time of current injection conclusion
        curr_end_index = curr_start_index + 1
        length = len(sweep_c)
        while sweep_c[curr_end_index] != 0:
            curr_end_index += 1
            if curr_end_index >= len(sweep_c):
                break
        curr_end_index -= 1


        # Get steady state current at the end of the trace
        count = 0
        sum_voltage = 0
        for j in range(curr_end_index - 200, curr_end_index):
            sum_voltage += sweep_y[j]
            count += 1
        steady_state_volt = sum_voltage / count

        # Get peak volt, index and time
        peak_volt = max(sweep_y)
        peak_index = np.argmax(sweep_y)
        peak_time = sweep_x[peak_index]

        dvdt_threshold = int(spinbox_dvdt.get())

        # # Get threshold by going backwards from voltage peak
        # k = peak_index
        # while sweep_y_d[k] < dvdt_threshold:
        #     k -= 1
        # while sweep_y_d[k] > dvdt_threshold:
        #     k-= 1
        # threshold_index = k
        # threshold_volt = sweep_y[threshold_index]
        # threshold_time = sweep_x[threshold_index]
        
        # get threshold thorugh convoluted method but technically more accurate to physiology
        k = current_injection_start(sweep_c) + 30
        sweep_y_d_2 = np.diff(sweep_y_d_filtered) / (1000 * np.diff(sweep_x_d))

        if use_window == 1:
            k = 0
            while sweep_x[k] < lower_window:
                k += 1
            
            while (sweep_y_d_filtered[k] < dvdt_threshold or sweep_y_d_2[k] < 0) and sweep_x[k] < upper_window:
                k += 1
            threshold_index = k
            threshold_volt = sweep_y[threshold_index]
            threshold_time = sweep_x[threshold_index] 
        else:
            while sweep_y_d_filtered[k] < dvdt_threshold or sweep_y_d_2[k] < 15:
                k += 1
            threshold_index = k
            threshold_volt = sweep_y[threshold_index]
            threshold_time = sweep_x[threshold_index]
        
        if check_threshold.get() == True:
            threshold_window(sweep_x, sweep_y, threshold_time, threshold_volt, "1s")
        
        else:
            window_check_bool = 1

    window_check_bool = 0
    
    # Find the deltas for rising phase
    halfwidth_volt = (peak_volt + threshold_volt) / 2
    rise_delta = peak_volt - threshold_volt
    rise_volt_10 = (rise_delta * .1) + threshold_volt
    rise_volt_90 = (rise_delta * .9) + threshold_volt
    
    # find the time points of rising phase
    k = threshold_index
    while sweep_y[k] < rise_volt_10:
        k += 1
    rise_time_10 = sweep_x[k]

    while sweep_y[k] < halfwidth_volt:
        k += 1
    halfwidth_start = sweep_x[k]

    while sweep_y[k] < rise_volt_90:
        k += 1
    rise_time_90 = sweep_x[k]

    # find time points of falling phase
    k = peak_index
    while sweep_y[k] > steady_state_volt:
        k += 1
    end_fall = sweep_x[k]
    end_fall_index = k
    
    # determine ahp points
    l = k
    # find the nearest steady state point
    while sweep_y_d_filtered[l] < 0: 
        l += 1
    
    while sweep_y[l] > steady_state_volt:
        l += 1
    ap_end_index = l

    ahp = 0
    ahp_index = 0
    ahp_array = sweep_y[end_fall_index:ap_end_index]
    ahp = min(ahp_array)
    ahp_index = np.argmin(ahp_array)
    fall_delta = ahp - peak_volt
    fall_volt_10 = (fall_delta * .1) + peak_volt
    fall_volt_90 = (fall_delta * .9) + peak_volt
    ahp_halfwidth_volt = (steady_state_volt + ahp) / 2

    # find ahp time points
    k = peak_index
    while sweep_y[k] > fall_volt_10:
        k += 1
    fall_time_10 = sweep_x[k]

    while sweep_y[k] > halfwidth_volt:
        k += 1
    halfwidth_end = sweep_x[k]

    while sweep_y[k] > fall_volt_90:
        k += 1
    fall_time_90 = sweep_x[k]

    while sweep_y[k] > ahp_halfwidth_volt:
        k +=1
    ahp_halfwidth_start = sweep_x[k]

    k = ahp_index
    while sweep_y[k] < ahp_halfwidth_volt:
        k += 1
    ahp_halfwidth_end = sweep_x[k]

    rise_time_raw = peak_time - threshold_time
    rise_time_10_90 = rise_time_90 - rise_time_10
    fall_time_raw = end_fall - peak_time
    fall_time_10_90 = fall_time_90 - fall_time_10
    halfwidth = halfwidth_end - halfwidth_start
    ahp_halfwidth = ahp_halfwidth_start - ahp_halfwidth_end
    rheobase = threshold_curr - holding_curr

    print("Relative Rheobase (nA): " + str(rheobase))
    f.write("Relative Rheobase (nA):, " + str(rheobase))
    f.write('\n')
    print("AP Peak (mV): " + str(peak_volt))
    f.write("AP Peak (mV):, " + str(peak_volt))
    f.write('\n')
    print("AP Amplitude (mV): " + str(peak_volt-threshold_volt))
    f.write("AP Amplitude (mV):, " + str(peak_volt-threshold_volt))
    f.write('\n')
    print("AP Voltage Threshold (mV): " + str(threshold_volt))
    f.write("AP Voltage Threshold (mV):, " + str(threshold_volt))
    f.write('\n')
    rise_time_raw = two_sig_figs(rise_time_raw)
    rise_time_10_90 = two_sig_figs(rise_time_10_90)
    print("AP Rise Time Raw (ms): " + str(rise_time_raw))
    f.write("AP Rise Time Raw (ms):, " + str(rise_time_raw))
    f.write('\n')
    print("AP Rise Time 10-90 (ms): " + str(rise_time_10_90))
    f.write("AP Rise Time 10-90 (ms):, " + str(rise_time_10_90))
    f.write('\n')
    halfwidth = two_sig_figs(halfwidth)
    print("AP Halfwidth (ms): " + str(halfwidth))
    f.write("AP Halfwidth (ms):, " + str(halfwidth))
    f.write('\n')
    fall_time_raw = two_sig_figs(fall_time_raw)
    fall_time_10_90 = two_sig_figs(fall_time_10_90)
    print("AP Falling Time Raw (ms): " + str(fall_time_raw))
    f.write("AP Falling Time Raw (ms):, " + str(fall_time_raw))
    f.write('\n')
    print("AP Falling Time 10-90 (ms): " + str(fall_time_10_90))
    f.write("AP Falling Time 10-90 (ms):, " + str(fall_time_10_90))
    f.write('\n')
    print("AHP Minimum (mV): " + str(ahp))
    f.write("AHP Minimum (mV):, " + str(ahp))
    f.write('\n')
    print("AHP Relative (mV): " + str(ahp - threshold_volt))
    f.write("AHP Relative (mV):, " + str(ahp - threshold_volt))
    f.write('\n')
    ahp_halfwidth = two_sig_figs(ahp_halfwidth)
    print("AHP half-width (ms): " + str(ahp_halfwidth))
    f.write("AHP half-width (ms):, " + str(ahp_halfwidth))
    f.write('\n')
    print("Upstroke-Downstroke ratio: " + str(rise_time_10_90 / fall_time_10_90))
    f.write("Upstroke-Downstroke ratio:, " + str(rise_time_10_90 / fall_time_10_90))
    f.write('\n')

    phase_plane(sweep_x_d, sweep_y_1, sweep_y_d, "1s")

    # Graphing single AP
    plt.clf()
    plt.grid()
    ax1 = plt.subplot()
    # ax2 = ax1.twinx()
    ax1.set_ylabel(abf.sweepLabelY)
    ax1.set_xlabel(abf.sweepLabelX)
    # ax2.set_ylabel(abf.sweepLabelC)
    ax1.plot(sweep_x, sweep_y, alpha=.5, label=" sweep %d voltage" % sweep_number)
    image_name = no_spaces(output_file_entry.get()) + "_rheo_1s_single_ap_graph.png"
    plt.title(image_name[:-4])
    image_path = os.path.join(final_directory, image_name)
    plt.savefig(image_path)


def phase_plane(sweep_x, sweep_y, sweep_y_d, step):
    global phase_plane_bool_5ms
    global phase_plane_bool_1s
    global output_file_path_pp_5ms
    global output_file_path_pp_1s
    global final_directory

    output_file_name = no_spaces(output_file_entry.get())
    output_file_name_pp = output_file_name + "_" + step + "_phase_plane_table.csv"
    if step == "5ms":
        phase_plane_bool_5ms = True
        output_file_path_pp_5ms = os.path.join(final_directory, output_file_name_pp)
        with open(output_file_path_pp_5ms, 'w') as b:
            b.write("time, V, dV/dt")
            b.write('\n')
            for i in range(len(sweep_y_d)):
                b.write(str(sweep_x[i]) + ", " + str(sweep_y[i]) + ", " + str(sweep_y_d[i]))
                b.write('\n')
    elif step == "1s":
        phase_plane_bool_1s = True
        output_file_path_pp_1s = os.path.join(final_directory, output_file_name_pp)
        with open(output_file_path_pp_1s, 'w') as b:
            b.write("time, V, dV/dt")
            b.write('\n')
            for i in range(len(sweep_y_d)):
                b.write(str(sweep_x[i]) + ", " + str(sweep_y[i]) + ", " + str(sweep_y_d[i]))
                b.write('\n')    
    plt.clf()
    plt.grid()
    ax1 = plt.subplot()
    # ax2 = ax1.twinx()
    ax1.set_ylabel("Derivative of Membrane Potential (mv/ms)")
    ax1.set_xlabel("Membrane Potential (mV)")
    # ax2.set_ylabel(abf.sweepLabelC)
    ax1.plot(sweep_y, sweep_y_d, alpha=.5)
    image_name = no_spaces(output_file_entry.get()) + "_" + step +"_phase_plane_plot.png"
    plt.title(image_name[:-4])
    image_path = os.path.join(final_directory, image_name)
    plt.savefig(image_path)


def callback():
    global phase_plane_bool_5ms
    global phase_plane_bool_1s
    global output_file_path_pp_5ms
    global final_directory
    global conversion_bool
    output_file_name = no_spaces(output_file_entry.get())
    output_folder_name = output_file_name + "_outputs"
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, output_folder_name)
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    output_file_path = os.path.join(final_directory, output_file_name + "_analyzed.csv")
    with open(output_file_path, 'w') as f:
        rmp(filename1, f)
        rheo_1s(filename2, f)
        rheo_4x(filename3, f)
        ramp_1s(filename4, f)
        ramp_4x(filename5, f)
        short_rheo_5ms(filename6, f)
        short_rheo_1s(filename7, f)
    os.system("start EXCEL.EXE " + output_file_path)
    if phase_plane_bool_5ms == True:
        os.system("start EXCEL.EXE " + output_file_path_pp_5ms)
        phase_plane_bool_5ms = False
    if phase_plane_bool_1s == True:
        os.system("start EXCEL.EXE " + output_file_path_pp_1s)
        phase_plane_bool_1s = False

#   Conversion
    # Metadata info
    if conversion_bool.get() == 1:
        df = pd.read_excel('bulk_abf_nwb_converter.xlsx')
        input_folder = current_directory + "\\inputs"
        if filename1 != "No File Chosen":
            df2 = pd.DataFrame({'File Name': [file_name_presentation(filename1)],
                    'Cell Id' : [cell_id.get()],
                    'Slice ID' : [slice_id.get()],
                    'Targeted Layer' : [targeted_layer.get()],
                    'Inferred Layer' : [inferred_layer.get()],
                    'Stimulus Type' : ["long_square"],
                    'Clamp Type' : ["current_clamp"],
                    'Session Description' : [session_description.get()],
                    'Lab Name' : [lab.get()],
                    'Institution Name' : [institution.get()],
                    'Experimenter Name' : [experimenter.get()],
                    'Subject ID' : [subject_id.get()],
                    'Species' : [species.get()],
                    'Sex' : [sex.get()],
                    'Date of Birth' : [date_of_birth.get()]
                    })
            df = pd.concat([df, df2], axis=0)
            shutil.copy(filename1, input_folder)
        if filename2 != "No File Chosen":
            df2 = pd.DataFrame({'File Name': [file_name_presentation(filename2)],
                    'Cell Id' : [cell_id.get()],
                    'Slice ID' : [slice_id.get()],
                    'Targeted Layer' : [targeted_layer.get()],
                    'Inferred Layer' : [inferred_layer.get()],
                    'Stimulus Type' : ["long_square"],
                    'Clamp Type' : ["current_clamp"],
                    'Session Description' : [session_description.get()],
                    'Lab Name' : [lab.get()],
                    'Institution Name' : [institution.get()],
                    'Experimenter Name' : [experimenter.get()],
                    'Subject ID' : [subject_id.get()],
                    'Species' : [species.get()],
                    'Sex' : [sex.get()],
                    'Date of Birth' : [date_of_birth.get()]
                    })
            df = pd.concat([df, df2], axis=0)
            shutil.copy(filename2, input_folder)
        if filename3 != "No File Chosen":
            df2 = pd.DataFrame({'File Name': [file_name_presentation(filename3)],
                    'Cell Id' : [cell_id.get()],
                    'Slice ID' : [slice_id.get()],
                    'Targeted Layer' : [targeted_layer.get()],
                    'Inferred Layer' : [inferred_layer.get()],
                    'Stimulus Type' : ["long_square"],
                    'Clamp Type' : ["current_clamp"],
                    'Session Description' : [session_description.get()],
                    'Lab Name' : [lab.get()],
                    'Institution Name' : [institution.get()],
                    'Experimenter Name' : [experimenter.get()],
                    'Subject ID' : [subject_id.get()],
                    'Species' : [species.get()],
                    'Sex' : [sex.get()],
                    'Date of Birth' : [date_of_birth.get()]
                    })
            df = pd.concat([df, df2], axis=0)
            shutil.copy(filename3, input_folder)
        if filename4 != "No File Chosen":
            df2 = pd.DataFrame({'File Name': [file_name_presentation(filename4)],
                    'Cell Id' : [cell_id.get()],
                    'Slice ID' : [slice_id.get()],
                    'Targeted Layer' : [targeted_layer.get()],
                    'Inferred Layer' : [inferred_layer.get()],
                    'Stimulus Type' : ["long_square"],
                    'Clamp Type' : ["current_clamp"],
                    'Session Description' : [session_description.get()],
                    'Lab Name' : [lab.get()],
                    'Institution Name' : [institution.get()],
                    'Experimenter Name' : [experimenter.get()],
                    'Subject ID' : [subject_id.get()],
                    'Species' : [species.get()],
                    'Sex' : [sex.get()],
                    'Date of Birth' : [date_of_birth.get()]
                    })
            df = pd.concat([df, df2], axis=0)
            shutil.copy(filename4, input_folder)
        if filename5 != "No File Chosen":
            df2 = pd.DataFrame({'File Name': [file_name_presentation(filename5)],
                    'Cell Id' : [cell_id.get()],
                    'Slice ID' : [slice_id.get()],
                    'Targeted Layer' : [targeted_layer.get()],
                    'Inferred Layer' : [inferred_layer.get()],
                    'Stimulus Type' : ["long_square"],
                    'Clamp Type' : ["current_clamp"],
                    'Session Description' : [session_description.get()],
                    'Lab Name' : [lab.get()],
                    'Institution Name' : [institution.get()],
                    'Experimenter Name' : [experimenter.get()],
                    'Subject ID' : [subject_id.get()],
                    'Species' : [species.get()],
                    'Sex' : [sex.get()],
                    'Date of Birth' : [date_of_birth.get()]
                    })
            df = pd.concat([df, df2], axis=0)
            shutil.copy(filename5, input_folder)
        if filename6 != "No File Chosen":
            df2 = pd.DataFrame({'File Name': [file_name_presentation(filename6)],
                    'Cell Id' : [cell_id.get()],
                    'Slice ID' : [slice_id.get()],
                    'Targeted Layer' : [targeted_layer.get()],
                    'Inferred Layer' : [inferred_layer.get()],
                    'Stimulus Type' : ["long_square"],
                    'Clamp Type' : ["current_clamp"],
                    'Session Description' : [session_description.get()],
                    'Lab Name' : [lab.get()],
                    'Institution Name' : [institution.get()],
                    'Experimenter Name' : [experimenter.get()],
                    'Subject ID' : [subject_id.get()],
                    'Species' : [species.get()],
                    'Sex' : [sex.get()],
                    'Date of Birth' : [date_of_birth.get()]
                    })
            df = pd.concat([df, df2], axis=0)
            shutil.copy(filename6, input_folder)
        if filename7 != "No File Chosen":
            df2 = pd.DataFrame({'File Name': [file_name_presentation(filename7)],
                    'Cell Id' : [cell_id.get()],
                    'Slice ID' : [slice_id.get()],
                    'Targeted Layer' : [targeted_layer.get()],
                    'Inferred Layer' : [inferred_layer.get()],
                    'Stimulus Type' : ["long_square"],
                    'Clamp Type' : ["current_clamp"],
                    'Session Description' : [session_description.get()],
                    'Lab Name' : [lab.get()],
                    'Institution Name' : [institution.get()],
                    'Experimenter Name' : [experimenter.get()],
                    'Subject ID' : [subject_id.get()],
                    'Species' : [species.get()],
                    'Sex' : [sex.get()],
                    'Date of Birth' : [date_of_birth.get()]
                    })
            df = pd.concat([df, df2], axis=0)
            shutil.copy(filename7, input_folder)
        df.to_excel("bulk_abf_nwb_converter.xlsx", index=False)
        # for j in range(og_len, i):
        #     df.iloc[j, 1] = cell_id.get()
        #     df.iloc[j, 2] = slice_id.get()
        #     df.iloc[j, 3] = targeted_layer.get()
        #     df.iloc[j, 4] = inferred_layer.get()
        #     df.iloc[i, 5] = "long_square"
        #     df.iloc[i, 6] = "current_clamp"
        #     df.iloc[j, 7] = session_description.get()
        #     df.iloc[j, 8] = lab.get()
        #     df.iloc[j, 9] = institution.get()
        #     df.iloc[j, 10] = experimenter.get()
        #     df.iloc[j, 11] = subject_id.get()
        #     df.iloc[j, 12] = species.get()
        #     df.iloc[j, 13] = sex.get()
        #     df.iloc[j, 14] = date_of_birth.get()
    print("Analysis Complete")
    return


filename1 = "No File Chosen"
filename2 = "No File Chosen"
filename3 = "No File Chosen"
filename4 = "No File Chosen"
filename5 = "No File Chosen"
filename6 = "No File Chosen"
filename7 = "No File Chosen"
final_directory = ""
output_file_path_pp_5ms = ""
output_file_path_pp_1s = ""
buttonClicked = False
phase_plane_bool_5ms = False
phase_plane_bool_1s = False

window = tk.Tk()
window.title("ABRACADABRA")
window.geometry('600x475')
try:
    window.iconbitmap(os.getcwd() + "\\ABRACADABRA.ico")
except:
    print("Icon not in correct directory, but not necessary")
conversion_bool = tk.IntVar()
spinval = tk.StringVar()
spinval.set("5")
spinbox_dvdt = tk.Spinbox(window, from_=1.0, to=100.0, textvariable=spinval, width=5)
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
output_file_name_variable = tk.StringVar()
output_file_entry = tk.Entry(window, textvariable=output_file_name_variable, width=40)
bool_reset_window = False
check_button_ram = 0
check_threshold = tk.BooleanVar()
window_check_bool = 0
upper_window = 0
lower_window = 0
use_window = 0
sweep_ram = 0
keep_window_open = 1

gui()
