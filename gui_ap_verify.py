import tkinter as tk
import tkinter.font as tkfont
from PIL import ImageTk, Image
import sys
import os


def ap_verified(ap_verify_window, ap_counts, spin_vars):
    """
    Update AP counts based on user verification and close the verification window.
    Parameters
    ----------
    ap_verify_window : tk.Toplevel or tk.Tk
        The window containing the AP count verification UI.
    ap_counts : list[int]
        List of calculated AP counts for each sweep, to be updated with verified counts.
    spin_vars : list[tk.StringVar]
        List of StringVar instances linked to the Spinbox widgets for user input of verified counts.
    
    Returns
    -------
    None
    """
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
    """Create a GUI window for verifying calculated action potential counts.
    
    Parameters
    ----------
    image_names : list[str]
        List of file paths to images showing detected APs for each sweep.
    ap_counts : list[int]
        List of calculated AP counts for each sweep, to be displayed and verified by the user.
    
     Returns
     -------
     list[int]
         Updated list of AP counts based on user verification.
     """
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

    # Shared font objects: reconfiguring their size in on_resize updates every widget using them.
    base_image_width = 320
    base_title_size, base_text_size, base_button_size = 16, 10, 12
    title_font = tkfont.Font(root=ap_verify_window, family="Verdana", size=base_title_size)
    text_font = tkfont.Font(root=ap_verify_window, family="Verdana", size=base_text_size)
    button_font = tkfont.Font(root=ap_verify_window, family="Verdana", size=base_button_size)

    # Equal column weights so the 8-column grid spans the window and centered widgets stay centered.
    for col in range(8):
        ap_verify_window.grid_columnconfigure(col, weight=1)

    verify_label = tk.Label(ap_verify_window, text="Verify Calculated Action Potential Counts", font=title_font)
    verify_label.grid(column=0, columnspan=8, row=0)

    photo_images = []
    image_labels = []
    pil_images = []
    for name in image_names:
        # Load fully into memory and release the file handle so the
        # temporary preview PNGs can be deleted afterwards (Windows locks open files).
        with Image.open(name) as img:
            pil_images.append(img.copy())
    
    for i in range(4):
        resized = pil_images[i].resize((320, 240), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized)
        photo_images.append(photo)

        image_label = tk.Label(ap_verify_window, image=photo)
        image_label.grid(column=i*2, columnspan=2, row=1)
        image_labels.append(image_label)

        calculated_label = tk.Label(ap_verify_window, text="Calculated Count: ", font=text_font)
        calculated_label.grid(column=i*2, row=2, sticky='e')

        count_label = tk.Label(ap_verify_window, text=str(ap_counts[i]), font=text_font)
        count_label.grid(column=(i*2)+1, row=2, sticky='w')

        manual_label = tk.Label(ap_verify_window, text="Verified Count: ", font=text_font)
        manual_label.grid(column=i*2, row=3, sticky='e')

        # Spinbox/Button widths are in characters, so they grow with their font size.
        spinbox = tk.Spinbox(ap_verify_window, from_=0.0, to=100.0, textvariable=spin_vars[i], width=5, font=text_font)
        spinbox.grid(column=(i*2)+1, row=3, sticky='w')

    verify_button = tk.Button(ap_verify_window, text="Verified!", width=10, bg="green", fg="black", font=button_font, command=lambda: ap_verified(ap_verify_window, ap_counts, spin_vars))
    verify_button.grid(row=4, column=0, columnspan=8, pady=10)

    
    def on_resize(event):
        """Handle window resize events to adjust the size of the displayed images while maintaining aspect ratio.
        Parameters
        ----------
        event : tk.Event
            The event object containing information about the resize event.
        
        Returns
        -------
        None
        """
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

            # Scale fonts (and therefore char-width widgets) with the image size.
            scale = new_width / base_image_width
            title_font.configure(size=max(8, round(base_title_size * scale)))
            text_font.configure(size=max(6, round(base_text_size * scale)))
            button_font.configure(size=max(7, round(base_button_size * scale)))
            verify_button.grid_configure(pady=max(4, round(10 * scale)))

    
    def on_closing():
        """Handle the window close event to ensure AP counts are updated based on user verification before closing."""
        ap_verified(ap_verify_window, ap_counts, spin_vars)
        ap_verify_window.destroy()



    ap_verify_window.bind("<Configure>", on_resize)
    ap_verify_window.protocol("WM_DELETE_WINDOW", on_closing)

    ap_verify_window.grab_set()
    ap_verify_window.wait_window()
    return ap_counts