import tkinter as tk
from PIL import ImageTk, Image
import sys
import os


def ap_verified(ap_verify_window, ap_counts, spin_vars):
    ap_counts[0] = int(spin_vars[0].get())
    ap_counts[1] = int(spin_vars[1].get())
    ap_counts[2] = int(spin_vars[2].get())
    ap_counts[3] = int(spin_vars[3].get())
    ap_verify_window.destroy()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def ap_count_window(image_names, ap_counts):
    global window_width
    try:
        ap_verify_window = tk.Toplevel()
    except tk.TclError:
        ap_verify_window = tk.Tk()
        ap_verify_window.withdraw()
    ap_verify_window.title("Verify Action Potential Counts")
    ap_verify_window.geometry("1280x400")   
    window_width = 1280

    try:   
        icon_path = resource_path("assets/ABRACADABRA.ico")
        ap_verify_window.iconbitmap(icon_path)
    except Exception:
        print("Icon Not found, continuing without it")

    spin_vars = [tk.StringVar(value=str(count)) for count in ap_counts]

    verify_label = tk.Label(ap_verify_window, text="Verify Calculated Action Potential Counts", font=("Verdana", 16))
    verify_label.grid(column=0, columnspan=8, row=0)

    photo_images = []
    image_labels = []
    pil_images = [Image.open(name) for name in image_names]
    
    for i in range(4):
        resized = pil_images[i].resize((320, 240), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized)
        photo_images.append(photo)

        image_label = tk.Label(ap_verify_window, image=photo)
        image_label.grid(column=i*2, columnspan=2, row=1)
        image_labels.append(image_label)

        calculated_label = tk.Label(ap_verify_window, text="Calculated Count: ", font=("Verdana", 10))
        calculated_label.grid(column=i*2, row=2, sticky='e')

        count_label = tk.Label(ap_verify_window, text=str(ap_counts[i]), font=("Verdana", 10))
        count_label.grid(column=(i*2)+1, row=2, sticky='w')

        manual_label = tk.Label(ap_verify_window, text="Verified Count: ", font=("Verdana", 10))
        manual_label.grid(column=i*2, row=3, sticky='e')

        spinbox = tk.Spinbox(ap_verify_window, from_=0.0, to=100.0, textvariable=spin_vars[i], width=5, font=("Verdana", 10))
        spinbox.grid(column=(i*2)+1, row=3, sticky='w')

    verify_button = tk.Button(ap_verify_window, text="Verified!", width=10, bg="green", fg="black", font=("Verdana", 12), command=lambda: ap_verified(ap_verify_window, ap_counts, spin_vars))
    verify_button.grid(row=4, column=0, columnspan=7, pady=10, sticky='s')

    
    def on_resize(event):
        global window_width
        if ap_verify_window.winfo_width() != window_width:
            window_width = ap_verify_window.winfo_width()
            new_width = window_width // 4  # or some other logic
            new_height = int(new_width * 0.75)

            if new_width <= 0 or new_height <= 0:
                return  # ignore resize events with invalid size

            for i in range(4):
                resized = pil_images[i].resize((new_width, new_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(resized)
                photo_images[i] = photo
                image_labels[i].config(image=photo)

    
    def on_closing():
        ap_verified(ap_verify_window, ap_counts, spin_vars)
        ap_verify_window.destroy()



    ap_verify_window.bind("<Configure>", on_resize)
    ap_verify_window.protocol("WM_DELETE_WINDOW", on_closing)

    ap_verify_window.grab_set()
    ap_verify_window.wait_window()
    return ap_counts