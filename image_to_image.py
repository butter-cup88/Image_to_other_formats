import os
import platform
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import pillow_heif
import ttkbootstrap as tb
from ttkbootstrap.constants import *

root = tb.Window(themename="cyborg")


# Register HEIC support for PIL
pillow_heif.register_heif_opener()

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Converter")
        self.root.geometry("900x650")
        self.root.resizable(False, False)

        self.file_paths = []
        self.other_formats_found = []
        self.converted_format = tk.StringVar(value="jpg")
        self.mode = tk.StringVar(value="One File")
        
        #--------------------heading-------------------
        tb.Label(root, text="Convert image files to other image formats", font=("Helvetica",20,"italic"), foreground="green").grid(row=0, column=0, columnspan=6, padx=75, pady=30)

        # ----- Mode Selection (Radio Buttons) -----
        mode_frame=tb.LabelFrame(root, text="Select one", bootstyle="info")
        mode_frame.grid(row=1, column=0, padx=35, pady=5, sticky="w", columnspan=6)
        
        # tb.Label(root, text="Select one:", bootstyle="info").grid(row=1, column=0, padx=15, pady=15, sticky="w")
        
        modes = [
            ("One File", "One File"),
            ("Multiple Files", "Multiple Files"),
            ("Folder (No Subfolders)", "Folder (No Subfolders)"),
            ("Folder (With Subfolders)", "Folder (With Subfolders)")
        ]
        for i, (text, value) in enumerate(modes):
            tb.Radiobutton(mode_frame, text=text, value=value, variable=self.mode, bootstyle="info").grid(
                row=0, column=i+1, padx=15, pady=25, sticky="w"
            )

        # ----- Format Selection (Radio Buttons) -----
        format_frame=tb.LabelFrame(root, text="Convert To:", bootstyle="info")
        format_frame.grid(row=2, column=0, padx=35, pady=5, sticky="w", columnspan=4)
        
        #tb.Label(root, text="Convert To:", bootstyle="info").grid(row=2, column=0, padx=15, pady=15, sticky="w")
        
        formats = ["jpeg", "png", "heic", "ico"]
        for i, fmt in enumerate(formats):
            tb.Radiobutton(format_frame, text=fmt.upper(), value=fmt, variable=self.converted_format, bootstyle="success").grid(
                row=0, column=i+1, padx=15, pady=25, sticky="w"
            )

        # ----- Buttons -----
        actions_frame=tb.LabelFrame(root, text="Actions", bootstyle="info")
        actions_frame.grid(row=2, column=4, padx=5, pady=5, sticky="w", columnspan=4)
        
        tb.Button(actions_frame, text="Browse", bootstyle="primary outline", command=self.select_files).grid(row=0, column=0, padx=15, pady=15)
        tb.Button(actions_frame, text="Convert", bootstyle="success outline", command=self.convert_images).grid(row=0, column=1, padx=15, pady=5)
        tb.Button(actions_frame, text="Clear", bootstyle="warning outline", command=self.clear_all).grid(row=0, column=2, padx=15, pady=5)
        tb.Button(actions_frame, text="Exit", bootstyle="danger outline", command=root.quit).grid(row=0, column=3, padx=15, pady=5)

        # ----- Treeviews -----
        self.file_tree = tb.Treeview(root, columns=("Path",), show="headings", height=10, bootstyle="info")
        self.file_tree.heading("Path", text="File Path")

        self.other_tree = tb.Treeview(root, columns=("Other Formats",), show="headings", height=5, bootstyle="secondary")
        self.other_tree.heading("Other Formats", text="Non-selected Image Formats Found")

        self.file_count_label = tb.Label(root, text="", bootstyle="inverse-info")
        self.progress = tb.Progressbar(root, mode="determinate", bootstyle="striped-success")

    def select_files(self):
        self.clear_trees()
        self.other_formats_found.clear()
        mode = self.mode.get()
        self.file_paths.clear()

        if mode == "One File":
            file = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.heic *.ico")])
            if file:
                self.file_paths = [file]
        elif mode == "Multiple Files":
            files = filedialog.askopenfilenames(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.heic *.ico")])
            if files:
                self.file_paths = list(files)
        elif "Folder" in mode:
            folder = filedialog.askdirectory()
            if folder:
                for root_dir, dirs, files in os.walk(folder):
                    for file in files:
                        ext = file.lower().split(".")[-1]
                        if ext in ["jpg", "jpeg", "png", "heic", "ico"]:
                            self.file_paths.append(os.path.join(root_dir, file))
                        else:
                            self.other_formats_found.append(f"{file} ({ext})")
                    if mode == "Folder (No Subfolders)":
                        break

        if self.file_paths:
            self.show_file_tree()
        else:
            messagebox.showwarning("No Selection", "No valid image files selected.")

    def show_file_tree(self):
        self.file_tree.grid(row=3, column=0, columnspan=8, padx=25, pady=5, sticky="nsew")
        for file in self.file_paths:
            self.file_tree.insert("", "end", values=(file,))
        self.file_count_label.config(text=f"Total Files Selected: {len(self.file_paths)}")
        self.file_count_label.grid(row=4, column=0, columnspan=8, pady=5)

        if self.other_formats_found:
            self.other_tree.grid(row=5, column=0, columnspan=8, padx=25, pady=5, sticky="nsew")
            for other in self.other_formats_found:
                self.other_tree.insert("", "end", values=(other,))

    def convert_images(self):
        if not self.file_paths:
            messagebox.showwarning("No Files", "Please select files first.")
            return

        out_format = self.converted_format.get().lower()
        destination_folder = None

        self.progress.grid(row=6, column=0, columnspan=8, padx=25, pady=10, sticky="ew")
        self.progress["value"] = 0
        self.progress["maximum"] = len(self.file_paths)
        converted_count = 0

        for file in self.file_paths:
            try:
                img = Image.open(file)

                folder = os.path.abspath(os.path.join(os.path.dirname(file), out_format))
                destination_folder = folder
                os.makedirs(folder, exist_ok=True)

                base_name = os.path.splitext(os.path.basename(file))[0]
                save_path = os.path.join(folder, f"{base_name}.{out_format}")

                if out_format == "heic":
                    heif_img = pillow_heif.from_pillow(img)
                    heif_img.save(
                        save_path,
                        quality=95
                    )
                else:
                    img.save(save_path, format=out_format.upper())

                converted_count += 1
            except Exception as e:
                print(f"Error converting {file}: {e}")
            self.progress["value"] += 1
            self.root.update_idletasks()

        # Open destination folder automatically
        if destination_folder and os.path.exists(destination_folder):
            self.open_folder(destination_folder)

        # Show message & reset fields if no other formats
        if not self.other_formats_found:
            messagebox.showinfo("Conversion Complete", f"Converted {converted_count} file(s) to {out_format.upper()}.\nNo other formats found.")
            self.clear_all()
        else:
            messagebox.showinfo("Conversion Complete", f"Converted {converted_count} file(s) to {out_format.upper()} format.\n"
                                                       f"Other formats found: {len(self.other_formats_found)}")

    def open_folder(self, path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            os.system(f'open "{path}"')
        else:  # Linux
            os.system(f'xdg-open "{path}"')

    def clear_trees(self):
        self.file_tree.delete(*self.file_tree.get_children())
        self.other_tree.delete(*self.other_tree.get_children())

    def clear_all(self):
        self.file_paths.clear()
        self.other_formats_found.clear()
        self.clear_trees()
        self.file_tree.grid_remove()
        self.other_tree.grid_remove()
        self.file_count_label.config(text="")
        self.file_count_label.grid_remove()
        self.progress.grid_remove()

    
app = ImageConverterApp(root)

    
    
root.mainloop()
