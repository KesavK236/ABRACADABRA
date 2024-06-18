import os
import pyabf
import pyabf.filter
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from uuid import uuid4
from scipy.signal import savgol_filter
from tkinter.filedialog import askopenfilename
from neuroconv.datainterfaces import AbfInterface


# compiling line
# pyinstaller -F --icon="ABF Analyzer Icon.ico" --noconsole ABRACADABRA.py


def gui():
    global output_file_entry
    global spinbox_dvdt
    global conversion_bool

    if conversion_bool.get() == 1:
        window.geometry('550x720')
    else:
        window.geometry('550x500')

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
    label_shortrheo_5ms = tk.Label(window, text="Short Rheo 5ms", font=("Arial", 10))
    label_shortrheo_1s = tk.Label(window, text="Short Rheo 1s", font=("Arial", 10))
    label_dvdt = tk.Label(window, text="Threshold dV/dt in mV/ms", font=("Arial", 10))
    label_title = tk.Label(window, text="ABRACADABRA", font=100)
    label_output_name = tk.Label(window, text="Output File Name:", font=("Arial", 10))
    output_file_entry = tk.Entry(window, textvariable=output_file_name_variable, width=40, justify="center")

    # conversion GUI Widgets
    check_conversion = tk.Checkbutton(window, text='Convert to NWB file', command=gui,variable=conversion_bool,
	    onvalue=1, offvalue=0)
    label_conversion = tk.Label(window, text="Conversion will take a few minutes", font=("Arial", 12))
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
    # label_spacer.grid(row=8, column=0)
    label_dvdt.grid(row=9, column=1, columnspan=2, sticky='E', pady=25)
    spinbox_dvdt.grid(row=9, column=3)
    check_conversion.grid(row=10, column=3)
    # label_spacer.grid(row=11, column=0)
    label_output_name.grid(row=25, column=3)
    output_file_entry.grid(row=26, column=2, columnspan=3, padx=20)
    button_enter.grid(row=27, column=3, pady=5)   

    if conversion_bool.get() == 1:
        label_cell_id.grid(row=12, column=1, columnspan=2, sticky='E')
        text_cell_id.grid(row=12, column=3, columnspan=2, sticky='W')
        label_slice_id.grid(row=13, column=1, columnspan=2, sticky='E')
        text_slice_id.grid(row=13, column=3, columnspan=2, sticky='W')
        label_target_layer.grid(row=14, column=1, columnspan=2, sticky='E')
        text_target_layer.grid(row=14, column=3, columnspan=2, sticky='W')
        label_inferred_layer.grid(row=15, column=1, columnspan=2, sticky='E')
        text_inferred_layer.grid(row=15, column=3, columnspan=2, sticky='W')
        label_session_description.grid(row=16, column=1, columnspan=2, sticky='E')
        text_session_description.grid(row=16, column=3, columnspan=2, sticky='W')
        label_lab.grid(row=17, column=1, columnspan=2, sticky='E')
        text_lab.grid(row=17, column=3, columnspan=2, sticky='W')
        label_institution.grid(row=18, column=1, columnspan=2, sticky='E')
        text_institution.grid(row=18, column=3, columnspan=2, sticky='W')
        label_experimenter.grid(row=19, column=1, columnspan=2, sticky='E')
        text_experimenter.grid(row=19, column=3, columnspan=2, sticky='W')
        label_subject_id.grid(row=20, column=1, columnspan=2, sticky='E')
        text_subject_id.grid(row=20, column=3, columnspan=2, sticky='W')
        label_species.grid(row=21, column=1, columnspan=2, sticky='E')
        text_species.grid(row=21, column=3, columnspan=2, sticky='W')
        label_sex.grid(row=22, column=1, columnspan=2, sticky='E')
        text_sex.grid(row=22, column=3, columnspan=2, sticky='W')
        label_date_of_birth.grid(row=23, column=1, columnspan=2, sticky='E')
        text_date_of_birth.grid(row=23, column=3, columnspan=2, sticky='W')
        label_conversion.grid(row=24, column=2, columnspan=3)
    else:
        label_spacer.grid(row=11, column=0, pady=25)

    window.mainloop()


def file_name_presentation(file_name):
    j = len(file_name) - 1
    while file_name[j] != "/" and j > -1:
        j -= 1
    return file_name[j + 1:len(file_name)]


def file_change1():
    global abf
    global filename1
    filename1 = askopenfilename()
    eval("f'{}'".format(filename1))
    gui()


def file_change2():
    global abf
    global filename2
    filename2 = askopenfilename()
    gui()


def file_change3():
    global abf
    global filename3
    filename3 = askopenfilename()
    gui()


def file_change4():
    global abf
    global filename4
    filename4 = askopenfilename()
    gui()


def file_change5():
    global abf
    global filename5
    filename5 = askopenfilename()
    gui()


def file_change6():
    global abf
    global filename6
    filename6 = askopenfilename()
    gui()


def file_change7():
    global abf
    global filename7
    filename7 = askopenfilename()
    gui()


def file_clear1():
    global abf
    global filename1
    filename1 = "No File Chosen"
    gui()


def file_clear2():
    global abf
    global filename2
    filename2 = "No File Chosen"
    gui()


def file_clear3():
    global abf
    global filename3
    filename3 = "No File Chosen"
    gui()


def file_clear4():
    global abf
    global filename4
    filename4 = "No File Chosen"
    gui()


def file_clear5():
    global abf
    global filename5
    filename5 = "No File Chosen"
    gui()


def file_clear6():
    global abf
    global filename6
    filename6 = "No File Chosen"
    gui()


def file_clear7():
    global abf
    global filename7
    filename7 = "No File Chosen"
    gui()


def clear_frame():
    for widgets in window.winfo_children():
        widgets.destroy()


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


def current_infection_start(sweep_c):
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
    sweep_y = savgol_filter(np.array(abf.sweepY), window_length=100, polyorder=2)
    sum_potentials = 0
    for i in range(len(sweep_x)):
        sum_potentials += sweep_y[i]
    resting_potential = sum_potentials / len(sweep_x)

    print("Resting Membrane Potential (mV): " + str(resting_potential))
    f.write("Resting Membrane Potential (mV), " + str(resting_potential))
    f.write('\n')

    plt.clf()
    ax1 = plt.subplot()
    ax1.set_ylabel(abf.sweepLabelY)
    ax1.set_xlabel(abf.sweepLabelX)
    ax1.plot(sweep_x, sweep_y, alpha=.5)
    plt.grid()
    image_name = no_spaces(output_file_entry.get()) + "_rmp_graph.png"
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
        sweep_y = savgol_filter(np.array(abf.sweepY), window_length=100, polyorder=2)
        sweep_c = np.array(abf.sweepC)

        # calculate derivative of sweep_y
        sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
        sweep_x_d = sweep_x[1:len(sweep_x)]

        # get time of current injection
        curr_start_index = current_infection_start(sweep_c)

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

        if sweep_c[curr_start_index + 1] > 0 and ap_bool == 0:
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
            image_path = os.path.join(final_directory, image_name)
            plt.savefig(image_path)
            image_made_bool = 1

    if hyper_pol_count > 0:
        input_res = hyper_pol_input_res / (10 ** 6)
        omega = chr(0x3a9)
        print("Average Input Resistance (M" + omega + "): " + str(input_res))
        f.write("Average Input Resistance (Mega Ohms), " + str(input_res))
        f.write('\n')
        print("Voltage Sag: " + str(average_sag))
        f.write("Voltage Sag, " + str(average_sag))
        f.write('\n')

    if ap_bool == 1:
        print("Current at Threshold (nA): " + str(current_threshold))
        f.write("Current at Threshold (nA), " + str(current_threshold))
        f.write('\n')
        print("Rheobase (nA): " + str(rheobase))
        f.write("Rheobase (nA), " + str(rheobase))
        f.write('\n')
        ap_delay = two_sig_figs(ap_delay)
        print("Time to Spike (ms): " + str(ap_delay))
        f.write("Time to Spike (ms), " + str(ap_delay))
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
        sweep_y = savgol_filter(np.array(abf.sweepY), window_length=100, polyorder=2)
        sweep_c = np.array(abf.sweepC)

        sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
        sweep_x_d = sweep_x[1:len(sweep_x)]

        curr_start_index = current_infection_start(sweep_c)

        j = curr_start_index + 30
        ap_found = 0
        finding_peak = 0
        ap_count = 0
        threshold_ram = 0

        # Graphing
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
        image_name = no_spaces(output_file_entry.get()) + "_rheo_" + str(i+1) + "x_graph.png"
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
        f.write("Number of Action Potentials in Rheo " + str(i + 1) + "x rheobase, " + str(ap_count))
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
        sweep_y = savgol_filter(np.array(abf.sweepY), window_length=100, polyorder=2)
        sweep_c = np.array(abf.sweepC)

        sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
        sweep_x_d = sweep_x[1:len(sweep_x)]

        # get time of current injection
        curr_start_index = current_infection_start(sweep_c)

        if sweep_c[curr_start_index + 1] > 0 and ap_bool == 0:
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
            image_path = os.path.join(final_directory, image_name)
            plt.savefig(image_path)
            image_made_bool = 1
    if ap_bool == 1:
        print("Current at Threshold (nA): " + str(threshold_curr))
        f.write("Current at Threshold (nA), " + str(threshold_curr))
        f.write('\n')
        print("Delta Current (nA): " + str(curr_delta))
        f.write("Delta Current(nA), " + str(curr_delta))
        f.write('\n')
        ap_delay = two_sig_figs(ap_delay)
        print("Time to Spike (ms): " + str(ap_delay))
        f.write("Time to Spike (ms), " + str(ap_delay))
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
        sweep_y = savgol_filter(np.array(abf.sweepY), window_length=100, polyorder=2)
        sweep_c = np.array(abf.sweepC)

        sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
        sweep_x_d = sweep_x[1:len(sweep_x)]

        curr_start_index = current_infection_start(sweep_c)

        j = curr_start_index + 30
        ap_found = 0
        finding_first = 0
        finding_peak = 0
        ap_count = 0
        threshold_ram = 0

        # find current end
        current_end = j
        while sweep_c[current_end] > 0:
            current_end += 1
        current_end = current_end - 2
        # Graphing
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
        image_path = os.path.join(final_directory, image_name)
        plt.savefig(image_path)

        while j < current_end:
            if sweep_y_d[j] >= threshold_dvdt and ap_found == 0 and finding_peak == 0 and finding_first:
                finding_first = 0
                ap_found = 1
                finding_peak = 1
                threshold_ram = sweep_y[j]
                # ax1.plot(sweep_x[j], sweep_y[j], marker="o", markersize="10", markeredgecolor="blue",
                #          markerfacecolor="blue")
            elif sweep_y_d[j] >= 0 and ap_found == 0 and finding_peak == 0 and finding_first == 0:

                ap_found = 1
                finding_peak = 1
                threshold_ram = sweep_y[j]
                # ax1.plot(sweep_x[j], sweep_y[j], marker="o", markersize="10", markeredgecolor="blue",
                #          markerfacecolor="blue")

            elif finding_peak == 1 and sweep_y_d[j] < 0 < sweep_y[j]:
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
        print("Number of Action Potentials in Ramp " + str(i + 1) + "x threshold: " + str(ap_count))
        f.write("Number of Action Potentials in Ramp " + str(i + 1) + "x threshold, " + str(ap_count))
        f.write('\n')


def short_rheo(file_name, f, step):
    global abf
    global spinbox_dvdt
    if file_name == "No File Chosen":
        return
    print("Short_Rheo_" + step + " Data:")
    f.write("Short_Rheo_" + step + " Data:")
    f.write('\n')
    abf = pyabf.ABF(file_name)
    sweep_number = -1
    ap_max = -1

    while ap_max < 0:
        sweep_number += 1
        abf.setSweep(sweep_number)
        sweep_y = savgol_filter(np.array(abf.sweepY), window_length=100, polyorder=2)
        ap_max = max(sweep_y)
    print("sweep number = " + str(sweep_number))

    sweep_x = np.array(abf.sweepX)
    sweep_y = savgol_filter(np.array(abf.sweepY), window_length=100, polyorder=2)
    sweep_y_raw = np.array(abf.sweepY)
    sweep_c = np.array(abf.sweepC)

    sweep_y_d = np.diff(sweep_y) / (1000 * np.diff(sweep_x))
    sweep_x_d = sweep_x[1:len(sweep_x)]
    sweep_y_1 = sweep_y[1:len(sweep_y)]

    phase_plane(sweep_x_d, sweep_y_1, sweep_y_d, step)
    # ax1 = plt.subplot()
    # ax1.set_ylabel(abf.sweepLabelY)
    # ax1.set_xlabel(abf.sweepLabelX)
    # ax1.plot(sweep_x, sweep_y, alpha=0.5)

    curr_start_index = current_infection_start(sweep_c)
    j = curr_start_index

    count = 0
    sum_voltage = 0
    for j in range(200, 400, 1):
        sum_voltage += sweep_y[j]
        count += 1
    base_volt = sum_voltage / count

    bool_processing = 1
    bool_threshold = 1
    bool_rise_start = 0
    bool_half_rise = 0
    bool_rise_end = 0
    bool_fall_start = 0
    bool_half_fall = 0
    bool_fall_10_end = 0
    bool_fall_end = 0
    bool_half_ahp_fall = 0
    bool_half_ahp_rise = 0
    holding_current = 0
    threshold_volt = 0
    curr_threshold = 0
    k = 0
    v_peak = 0
    v_peak_index = 0
    ahp = 0
    ahp_index = 0
    peak_time = 0
    end_fall = 0
    ahp_time = 0
    threshold_dvdt = int(spinbox_dvdt.get())

    while k < len(sweep_x):
        if sweep_y[k] > v_peak:
            v_peak = sweep_y[k]
            v_peak_index = k
            peak_time = sweep_x[k]
        k += 1

    k = v_peak_index
    while k < len(sweep_x):
        if sweep_y[k] < ahp:
            ahp = sweep_y[k]
            ahp_index = k
            ahp_time = sweep_x[k]
        k += 1

    k = 0
    dv_peak = 0
    while k < len(sweep_y_d):
        if sweep_y_d[k] > dv_peak:
            dv_peak = sweep_y_d[k]
        k += 1

    # rakesh threshold
    threshold_dvdt = dv_peak / 10

    halfwidth_start = 0
    halfwidth_end = 0
    ahp_halfwidth_start = 0
    ahp_halfwidth_end = 0
    threshold_time = 0

    rise_time_start_10 = 0
    rise_time_end_90 = 0
    fall_time_start_10 = 0
    fall_time_end_90 = 0
    v_rising_delta = 0
    rise_time_10_start_index = 0
    rise_time_90_end_index = 0
    v_falling_delta = 0
    fall_time_10_start_index = 0
    fall_time_90_end_index = 0
    halfwidth_volt = 0
    ahp_halfwidth_volt = 0

    # Graphing
    plt.clf()
    plt.grid()
    ax1 = plt.subplot()
    # ax2 = ax1.twinx()
    ax1.set_ylabel(abf.sweepLabelY)
    ax1.set_xlabel(abf.sweepLabelX)
    # ax2.set_ylabel(abf.sweepLabelC)
    ax1.plot(sweep_x, sweep_y, alpha=.5, label=" sweep %d voltage" % sweep_number)
    plt.legend()
    image_name = no_spaces(output_file_entry.get()) + "_short_rheo_" + step + "_graph.png"
    image_path = os.path.join(final_directory, image_name)
    plt.savefig(image_path)
    # # ax1.plot(xhat, yhat, alpha=.5, label=" sweep %d voltage" % sweep_number)
    # ax2.plot(sweep_x, sweep_c, alpha=.5, label="sweep %d current" % sweep_number, color='green')
    # ax1.plot(sweep_x[v_peak_index], sweep_y[v_peak_index], marker="o", markersize="10", markeredgecolor="green",
    #          markerfacecolor="green")
    # ax1.plot(sweep_x[ahp_index], sweep_y[ahp_index], marker="o", markersize="10", markeredgecolor="red",
    #          markerfacecolor="red")
    #

    while j < len(sweep_x_d) - 15 and bool_processing:
        if sweep_y_d[j] > threshold_dvdt and bool_threshold:
            bool_threshold = 0
            bool_rise_start = 1
            threshold_volt = sweep_y[j]
            curr_threshold = sweep_c[curr_start_index + 1]
            holding_current = sweep_c[curr_start_index - 5]
            threshold_time = sweep_x[j]

            v_rising_delta = v_peak - threshold_volt
            rise_time_10_start_index = 0.1 * v_rising_delta + threshold_volt
            rise_time_90_end_index = 0.9 * v_rising_delta + threshold_volt
            v_falling_delta = threshold_volt - v_peak
            fall_time_10_start_index = 0.1 * v_falling_delta + v_peak
            fall_time_90_end_index = 0.9 * v_falling_delta + v_peak
            halfwidth_volt = (threshold_volt + v_peak) / 2
            ahp_halfwidth_volt = (threshold_volt + ahp) / 2

        if sweep_y[j] >= rise_time_10_start_index and bool_rise_start:
            bool_rise_start = 0
            bool_half_rise = 1
            rise_time_start_10 = sweep_x[j]

        elif sweep_y[j] >= halfwidth_volt and bool_half_rise and not bool_rise_start:
            bool_half_rise = 0
            bool_rise_end = 1
            halfwidth_start = sweep_x[j]

        elif sweep_y[j] >= rise_time_90_end_index and bool_rise_end and not bool_half_rise:
            bool_rise_end = 0
            bool_fall_start = 1
            rise_time_end_90 = sweep_x[j]

        elif j > v_peak_index and sweep_y[j] <= fall_time_10_start_index and bool_fall_start and not bool_rise_end:
            bool_fall_start = 0
            bool_half_fall = 1
            fall_time_start_10 = sweep_x[j]

        elif sweep_y[j] <= halfwidth_volt and bool_half_fall and not bool_fall_start:
            bool_half_fall = 0
            bool_fall_10_end = 1
            halfwidth_end = sweep_x[j]

        elif sweep_y[j] <= fall_time_90_end_index and bool_fall_10_end and not bool_half_fall:
            bool_fall_10_end = 0
            bool_fall_end = 1
            fall_time_end_90 = sweep_x[j]

        elif sweep_y[j] <= threshold_volt and bool_fall_end and not bool_fall_10_end:
            bool_fall_end = 0
            bool_half_ahp_fall = 1
            end_fall = sweep_x[j]

        elif sweep_y[j] <= ahp_halfwidth_volt and bool_half_ahp_fall and not bool_fall_end:
            bool_half_ahp_fall = 0
            bool_half_ahp_rise = 1
            ahp_halfwidth_start = sweep_x[j]

        elif j > ahp_index and sweep_y[j] >= ahp_halfwidth_volt and bool_half_ahp_rise and not bool_half_fall:
            bool_half_ahp_rise = 0
            bool_processing = 0
            ahp_halfwidth_end = sweep_x[j]

        j += 1

    # plt.show()

    rise_time_raw = peak_time - threshold_time
    rise_time_10_90 = rise_time_end_90 - rise_time_start_10
    fall_time_raw = end_fall - peak_time
    fall_time_10_90 = fall_time_end_90 - fall_time_start_10
    halfwidth = halfwidth_end - halfwidth_start
    ahp_halfwidth = ahp_halfwidth_start - end_fall
    rheobase = curr_threshold - holding_current

    print("Short Threshold Current (nA): " + str(curr_threshold))
    f.write("Short Threshold Current (nA), " + str(curr_threshold))
    f.write('\n')
    print("Short Rheobase (nA): " + str(rheobase))
    f.write("Short Rheobase (nA), " + str(rheobase))
    f.write('\n')
    print("AP Peak (mV): " + str(v_peak))
    f.write("AP Peak (mV), " + str(v_peak))
    f.write('\n')
    print("AP Amplitude (mV): " + str(v_peak-threshold_volt))
    f.write("AP Amplitude (mV), " + str(v_peak-threshold_volt))
    f.write('\n')
    print("AP Voltage Threshold (mV): " + str(threshold_volt))
    f.write("AP Voltage Threshold (mV), " + str(threshold_volt))
    f.write('\n')
    rise_time_raw = two_sig_figs(rise_time_raw)
    rise_time_10_90 = two_sig_figs(rise_time_10_90)
    print("AP Rise Time Raw (ms): " + str(rise_time_raw))
    f.write("AP Rise Time Raw (ms), " + str(rise_time_raw))
    f.write('\n')
    print("AP Rise Time 10-90 (ms): " + str(rise_time_10_90))
    f.write("AP Rise Time 10-90 (ms), " + str(rise_time_10_90))
    f.write('\n')
    halfwidth = two_sig_figs(halfwidth)
    print("AP Halfwidth (ms): " + str(halfwidth))
    f.write("AP Halfwidth (ms), " + str(halfwidth))
    f.write('\n')
    fall_time_raw = two_sig_figs(fall_time_raw)
    fall_time_10_90 = two_sig_figs(fall_time_10_90)
    print("AP Falling Time Raw (ms): " + str(fall_time_raw))
    f.write("AP Falling Time Raw (ms), " + str(fall_time_raw))
    f.write('\n')
    print("AP Falling Time 10-90 (ms): " + str(fall_time_10_90))
    f.write("AP Falling Time 10-90 (ms), " + str(fall_time_10_90))
    f.write('\n')
    print("AP Minimum (mV): " + str(ahp))
    f.write("AP Minimum (mV), " + str(ahp))
    f.write('\n')
    print("AHP (mV): " + str(ahp - threshold_volt))
    f.write("AHP (mV), " + str(ahp - threshold_volt))
    f.write('\n')
    ahp_halfwidth = two_sig_figs(ahp_halfwidth)
    print("AHP half-width (ms): " + str(ahp_halfwidth))
    f.write("AHP half-width (ms), " + str(ahp_halfwidth))
    f.write('\n')
    print("Upstroke-Downstroke ratio: " + str(rise_time_10_90 / fall_time_10_90))
    f.write("Upstroke-Downstroke ratio:, " + str(rise_time_10_90 / fall_time_10_90))
    f.write('\n')


def phase_plane(sweep_x, sweep_y, sweep_y_d, step):
    global phase_plane_bool_5ms
    global phase_plane_bool_1s
    global output_file_path_pp_5ms
    global output_file_path_pp_1s
    global final_directory

    output_file_name = no_spaces(output_file_entry.get())
    output_file_name_pp = output_file_name + "_" + step + "_phase_plane_table.csv"
    if step == "5ms":
        phase_plane_bool_5ms = 1
        output_file_path_pp_5ms = os.path.join(final_directory, output_file_name_pp)
        with open(output_file_path_pp_5ms, 'w') as b:
            b.write("time, V, dV/dt")
            b.write('\n')
            for i in range(len(sweep_y_d)):
                b.write(str(sweep_x[i]) + ", " + str(sweep_y[i]) + ", " + str(sweep_y_d[i]))
                b.write('\n')
    elif step == "1s":
        phase_plane_bool_1s = 1
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
    ax1.set_ylabel("dV/dt")
    ax1.set_xlabel("V")
    # ax2.set_ylabel(abf.sweepLabelC)
    ax1.plot(sweep_y, sweep_y_d, alpha=.5)
    image_name = no_spaces(output_file_entry.get()) + "_" + step +"_phase_plane_plot.png"
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
        short_rheo(filename6, f, "5ms")
        short_rheo(filename7, f, "1s")
    os.system("start EXCEL.EXE " + output_file_path)
    if phase_plane_bool_5ms == 1:
        os.system("start EXCEL.EXE " + output_file_path_pp_5ms)
        phase_plane_bool_5ms = 0
    if phase_plane_bool_1s == 1:
        os.system("start EXCEL.EXE " + output_file_path_pp_1s)
        phase_plane_bool_1s = 0

#     Conversion
    # Metadata info
    if conversion_bool.get() == 1:
        recording_sessions = []
        file_paths = []
        if filename1 != "No File Chosen":
            file_paths.append(filename1)
            session = {
                "abf_file_name": file_name_presentation(filename1),
                "stimulus_type": "long_square",
                "icephys_experiment_type": "current_clamp"
            }
            recording_sessions.append(session)
        if filename2 != "No File Chosen":
            file_paths.append(filename2)
            session = {
                "abf_file_name": file_name_presentation(filename2),
                "stimulus_type": "long_square",
                "icephys_experiment_type": "current_clamp"
            }
            recording_sessions.append(session)
        if filename3 != "No File Chosen":
            file_paths.append(filename3)
            session = {
                "abf_file_name": file_name_presentation(filename3),
                "stimulus_type": "long_square",
                "icephys_experiment_type": "current_clamp"
            }
            recording_sessions.append(session)
        if filename4 != "No File Chosen":
            file_paths.append(filename4)
            session = {
                "abf_file_name": file_name_presentation(filename4),
                "stimulus_type": "long_square",
                "icephys_experiment_type": "current_clamp"
            }
            recording_sessions.append(session)
        if filename5 != "No File Chosen":
            file_paths.append(filename5)
            session = {
                "abf_file_name": file_name_presentation(filename5),
                "stimulus_type": "long_square",
                "icephys_experiment_type": "current_clamp"
            }
            recording_sessions.append(session)
        if filename6 != "No File Chosen":
            file_paths.append(filename6)
            session = {
                "abf_file_name": file_name_presentation(filename6),
                "stimulus_type": "long_square",
                "icephys_experiment_type": "current_clamp"
            }
            recording_sessions.append(session)
        if filename7 != "No File Chosen":
            file_paths.append(filename7)
            session = {
                "abf_file_name": file_name_presentation(filename7),
                "stimulus_type": "long_square",
                "icephys_experiment_type": "current_clamp"
            }
            recording_sessions.append(session)

        icephys_metadata = {
            "cell_id": cell_id.get(),
            "slice_id": slice_id.get(),
            "targeted_layer": targeted_layer.get(),
            "inferred_layer": inferred_layer.get(),
            "recording_sessions": recording_sessions
        }

        # Instantiate data interface
        interface = AbfInterface(
            file_paths=file_paths,
            icephys_metadata=icephys_metadata
        )

        # Get metadata from source data and modify any values you want
        metadata = interface.get_metadata()
        metadata['NWBFile'].update(
            identifier=str(uuid4()),
            session_description=session_description.get(),
            lab=lab.get(),  # <-- optional
            institution=institution.get(),  # <-- optional
            experimenter=[experimenter.get()]  # <-- optional
        )
        metadata["Subject"] = dict(
            subject_id=subject_id.get(),
            species=species.get(),
            sex=sex.get(),
            date_of_birth=date_of_birth.get() + "T00:00:00"
        )

        # Run conversion
        interface.run_conversion(nwbfile_path=final_directory + "/" + output_file_name + ".nwb", metadata=metadata)
        print("converted to NWB")
    print("Done")
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
phase_plane_bool_5ms = 0
phase_plane_bool_1s = 0

window = tk.Tk()
window.title("ABRACADABRA")
window.geometry('550x500')
window.iconbitmap("ABRACADABRA.ico")
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

gui()
