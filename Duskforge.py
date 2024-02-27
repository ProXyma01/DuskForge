import os
import sys
import tkinter as tk
import shutil
import json
import threading
import subprocess
import gdown
from tkinter import filedialog, ttk, messagebox
from zipfile import ZipFile
from requests.exceptions import Timeout
from PIL import Image, ImageTk
import requests
import ctypes

if getattr(sys, 'frozen', False): 
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__)) 

addon_json_path = os.path.join(bundle_dir, 'json', 'addon_wotlk_db_url.json')
patch_json_path = os.path.join(bundle_dir, 'json', 'patch_wotlk_db_url.json')
path_ico_ge = os.path.join(bundle_dir, 'source', 'lang_geo.ico')
path_ico_en = os.path.join(bundle_dir, 'source', 'lang_en.ico')

with open(addon_json_path, 'r') as addon_file:
    addon_db_url = json.load(addon_file)

with open(patch_json_path, 'r') as patch_file:
    patch_db_url = json.load(patch_file)

PATCH_NAMES = [patch["Name"] for patch in patch_db_url]
CONFIG_FILE = "config.json"

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
            json.dump(config, file)
        FILE_ATTRIBUTE_HIDDEN = 0x02

        ctypes.windll.kernel32.SetFileAttributesW(CONFIG_FILE, FILE_ATTRIBUTE_HIDDEN)
    except PermissionError as e:
        print(f"Error saving configuration: {e}")
    except Exception as e:
        print(f"An error occurred while saving configuration: {e}")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def down_addon(url, filename, progress_var, timeout=30):
    try:
        with requests.get(url, stream=True, timeout=timeout) as req:
            total_len = int(req.headers.get('content-length'))
            dl = 0
            block_size = 1024

            with open(filename, 'wb') as file:
                for data in req.iter_content(block_size):
                    dl += len(data)
                    file.write(data)
                    progress = int(100 * dl / total_len)
                    progress_var.set(progress)

        return True
    except Timeout:
        messagebox.showwarning("Request Time out, Try Again Later.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def down_patch(url, filename):
    try:
        print(f"Downloading Started, Don't Close this window.")
        gdown.download(url, filename, quiet=True)
        print(f"Download of {filename} completed successfully!")
        return True
    except Exception as e:
        print(f"An error occurred during the download of {filename}: {e}")
        return False


def extract_zip(zip_file, path):
    try:
        with ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(path)
        ext_content = os.listdir(path)
        if len(ext_content) == 1 and os.path.isdir(os.path.join(path, ext_content[0])):
            sub_directory = os.path.join(path, ext_content[0])
            for item in os.listdir(sub_directory):
                item_path = os.path.join(sub_directory, item)
                if os.path.isfile(item_path):
                    shutil.move(item_path, path)
                elif os.path.isdir(item_path):
                    shutil.move(item_path, os.path.join(path, item))
            os.rmdir(sub_directory)

        return True

    except Exception as e:
        print(e)
        return False

current_language = "ge"

def change_language():

    global current_language

    if current_language == "ge":
        current_language = "en"
        language_button.config(image=img_lang_en)
        download_button_addon["text"] = "ადონების გადმოწერა"
        download_button_patches["text"] = "პაჩების გადმოწერა"
        default_location_button["text"] = "აირჩიე WOW ფოლდერის ლოკაცია"
        check_detection_button["text"] = "შეამოწმე გადმოწერილები"
        launch_wow_button["text"] = "დაიწყე თამაში"
    else:
        current_language = "ge"
        language_button.config(image=img_lang_geo)
        download_button_addon["text"] = "Download Addons"
        download_button_patches["text"] = "Download Patches"
        default_location_button["text"] = "Choose WOW Folder Location"
        check_detection_button["text"] = "Check Downloads"
        launch_wow_button["text"] = "Start The Game"

def choose_default_location():
    wow_folder_path = filedialog.askdirectory()
    if not wow_folder_path or isinstance(wow_folder_path, tuple):
        return
    
    default = os.path.join(wow_folder_path)
    default_location = os.path.join(wow_folder_path, "Interface", "Addons")
    default_location_patches = os.path.join(wow_folder_path, "Data")
    config["default_location_patches"] = default_location_patches
    config["default_location"] = default_location
    config["default"] = default
    
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    
    save_config(config)
    
    check_detection_button["state"] = "normal"

def delete_patch(file_name):
    try:
        os.remove(os.path.join(config.get("default_location_patches"), file_name))
        label_button_map[file_name][0].destroy()
        label_button_map[file_name][1].destroy()
        label_button_map[file_name][2].destroy()
        del label_button_map[file_name]
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete {file_name}: {e}")

def toggle_patch(patch_name, com_btn):
    current_path = os.path.join(config.get("default_location_patches"), patch_name)
    new_path = os.path.join(config.get("default_location_patches"), "~" + patch_name)
    if os.path.exists(current_path):
        os.rename(current_path, new_path)
        com_btn.config(text="Resume")
    else:
        os.rename(new_path, current_path)
        com_btn.config(text="Pause")

def comment_patch(patch_name, comment_button):
    if patch_name[0] == "~":
        toggle_patch(patch_name[1:], comment_button)
    else:
        toggle_patch(patch_name, comment_button)

def show_patch_det_win(det_win, patch_names):
    global no_patches_label, label_button_map

    for widget in det_win.winfo_children():
        widget.destroy()
    label_button_map = {}

    if not patch_names:
        no_patches_label = ttk.Label(det_win, text="No patches are installed", font=("Arial", 14))
        no_patches_label.pack(pady=35)
    else:
        for i, patch_name in enumerate(patch_names):
            label = ttk.Label(det_win, text=patch_name)
            label.grid(row=i, column=0, padx=10, pady=3)

            delete_button = ttk.Button(det_win, text="X", command=lambda p=patch_name: delete_patch(p))
            delete_button.grid(row=i, column=1, padx=10, pady=3)

            comment_button_text = "Pause" if patch_name[0] != "~" else "Resume"
            comment_button = ttk.Button(det_win, text=comment_button_text)            
            comment_button.grid(row=i, column=2, padx=10, pady=3)
            comment_button.config(command=lambda p=patch_name, b=comment_button: comment_patch(p, b))

            label_button_map[patch_name] = (label, delete_button, comment_button)


def detection_window():
    chosen_location = config.get("default_location", "")

    if not chosen_location:
        check_detection_button["state"] = "disable"
    else:
        check_detection_button["state"] = "normal"
        downloaded_patches = []

        patch_directory = config.get("default_location_patches")
        if os.path.exists(patch_directory) and os.path.isdir(patch_directory):
            downloaded_patches = [ patch 
                for patch in os.listdir(patch_directory) 
                    if patch.startswith("PATCH-") or patch.startswith("~PATCH-") and patch.endswith(".MPQ")]
        patch_num = len(downloaded_patches)
        win_height = 100 + patch_num * 50

        det_win = tk.Toplevel()

        det_win.title("Delete Patches")
        det_win.geometry(f"430x{win_height}")
        det_win.grab_set()
        show_patch_det_win(det_win, downloaded_patches)

def download_patches():
    loading_animation.pack(side="bottom", pady=(0,10))
    chosen_location = config.get("default_location_patches", "")
    if not chosen_location:
        loading_animation.pack_forget()
        if current_language == "ge":
            messagebox.showwarning("Choose WoW folder Location", "Choose the WoW folder Location for Downloading Patches.")
            return
        elif current_language == "en":
            messagebox.showwarning("აირჩიე WOW ფოლდერის ლოკაცია", "აირჩიე შენი WOW ფოლდერის ლოკაცია პაჩების გადმოსაწერად.")
            return

    downloaded_patches = []

    def down_p(patch):
        patch_name = patch["Name"]
        patch_url = patch["Url"]
        patch_file = os.path.join(chosen_location, patch_name)
        success = down_patch(patch_url, patch_file)

        if success:
            downloaded_patches.append(patch_name)


    def download_thread():
        loading_animation.start()
        for patch in patch_db_url:
            if patch.get("var") is not None and patch["var"].get():
                down_p(patch)
                patch["var"].set(False)

        window.after(0, show_patch_result)

    def show_patch_result():
        loading_animation.stop()
        loading_animation.pack_forget()  
        if current_language == "ge":
            if downloaded_patches:
                patch_names = ', '.join(downloaded_patches)
                messagebox.showinfo("Done!", f"Patches '{patch_names}' were Downloaded and installed successfully!")
            else:
                messagebox.showwarning("Mark patch", "Mark patch to Download")
        elif current_language == "en":
            if downloaded_patches:
                patch_names = ', '.join(downloaded_patches)
                messagebox.showinfo("პროცესი დასრულდა!", f"პაჩები '{patch_names}' გადმოწერა და დაყენდა წარმატებით!")
            else:
                messagebox.showwarning("მონიშნე პაჩები", "მონიშნე პაჩები გადმოსაწერად.")

    threading.Thread(target=download_thread).start()



def check_addon_selection(db, button):
    for addon in db:
        if addon["var"].get():
            button["state"] = "normal"
            return
    button["state"] = "disabled"

def download_addons():
    chosen_location = config.get("default_location", "")
    if current_language == "ge":
        if not chosen_location:
            messagebox.showwarning("Choose WOW folder Location", "Choose the WoW folder Location for Downloading Addons.")
            return
    elif current_language == "en":
        if not chosen_location:
            messagebox.showwarning("აირჩიეთ თქვენი WOW ფოლდერის ლოკაცია.", "აირჩიეთ თქვენი WOW ფოლდერის ლოკაცია ადმონების გადმოსაწერად.")
            return

    downloaded_addons = []

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(window, variable=progress_var, maximum=100)
    progress_bar.pack(side="bottom", pady=(0, 10)) 

    def download_thread():
        for addon in addon_db_url:
            if addon.get("var").get():
                addon_name = addon["Name"]
                addon_folder = os.path.join(chosen_location)
                os.makedirs(addon_folder, exist_ok=True)
                addon_zip = os.path.join(addon_folder, addon_name + ".zip")
                success = down_addon(addon["Url"], addon_zip, progress_var)

                if success:
                    success = extract_zip(addon_zip, addon_folder)
                    os.remove(addon_zip)
                    
                addon["var"].set(False)
                if success:
                    downloaded_addons.append(addon_name)
                progress_var.set(0) 

        window.after(0, show_result)

    def show_result():
        progress_bar.pack_forget() 
        if current_language == "ge":
            if downloaded_addons:
                addon_names = ', '.join(downloaded_addons)
                messagebox.showinfo("Done!", f"Addons '{addon_names}' were Downloaded and Installed successfully!")
        elif current_language == "en":
            if downloaded_addons:
                addon_names = ', '.join(downloaded_addons)
                messagebox.showinfo("Done!", f"ადონები '{addon_names}' გადმოიწერა და დაყენდა წარმატებით!")
            
    threading.Thread(target=download_thread).start()


def launch_wow():
    choose_location = config.get("default")
    if not choose_location:
        if current_language == "ge":
            messagebox.showwarning("Choose WoW folder Location", "No Location Chosen")
        elif current_language == "en":
            messagebox.showwarning("აირჩიე WOW ფოლდერის ლოკაცია", "ლოკაცია არჩეული არ არის")
    else:
        wow_path =  os.path.join(config.get("default"), "Wow.exe")
        if os.path.exists(wow_path):
            subprocess.Popen(wow_path)
        else:
            if current_language == "ge":
                messagebox.showerror("Error", "Wow.exe not found!")
            elif  current_language == "en":
                messagebox.showerror("Error", "ფაილი Wow.exe არ არსებობს!")

config = load_config()

window = tk.Tk()
window.title("Duskforge (by R00T)")
window.geometry("1000x800")
style = ttk.Style()
style.configure("TFrame", background="#ececec")
style.configure("TButton", background="#3f51b5", foreground="black", font=("Arial", 12, "bold"), padding=10)
style.map("TButton", background=[("active", "#5677fc")])
style.configure("TLabel", background="#ececec", font=("Arial", 12))
style.configure("TCheckbutton", background="#ececec", font=("Arial", 12))


img_lang_en = ImageTk.PhotoImage(Image.open(path_ico_en).resize((30, 20)))
img_lang_geo = ImageTk.PhotoImage(Image.open(path_ico_ge).resize((30, 20)))


default_location_button = ttk.Button(window, text="Choose WOW Folder Location", command=choose_default_location)
default_location_button.pack(side="bottom", pady=(0, 8)) 

launch_wow_button = ttk.Button(window, text="Start The Game", command=launch_wow)
launch_wow_button.pack(side="bottom", pady=10)

check_detection_button = ttk.Button(window, text="Check Downloads", command=detection_window)
check_detection_button.pack(side="top", padx=10, pady=10)

language_button = ttk.Button(window, image=img_lang_geo, command=change_language, padding=0)
language_button.place(relx=1.0, rely=0.95, anchor="se", x=-4, y=38)

addon_frame = ttk.Frame(window, padding=20, width=300, height=400)
addon_frame.place(relx=0, rely=0, anchor="nw")
addon_frame.place_configure(x=50, y=30)


ttk.Label(addon_frame, text="Addons", font=("Arial", 14, "bold")).pack(pady=10)
ttk.Separator(addon_frame, orient="horizontal").pack(fill="x", padx=10, pady=(0, 10))


addon_vars = []

for addon in addon_db_url:
    addon_var = tk.BooleanVar()
    addon_vars.append(addon_var)
    addon_checkbox = ttk.Checkbutton(addon_frame, text=addon["Name"], variable=addon_var)
    addon_checkbox.pack(anchor="w")
    addon_var.trace_add("write", lambda *args: check_addon_selection(addon_db_url, download_button_addon))
    addon["var"] = addon_var


patch_frame = ttk.Frame(window, padding=20, width=300, height=400)
patch_frame.place(relx=1, rely=0, anchor="ne")
patch_frame.place_configure(x=-50, y=30)


ttk.Label(patch_frame, text="Patches", font=("Arial", 14, "bold")).pack(pady=10)
ttk.Separator(patch_frame, orient="horizontal").pack(fill="x", padx=10, pady=(0, 10))

patch_vars = []

for patch in patch_db_url:
    patch_var = tk.BooleanVar()
    patch_vars.append(patch_var)
    patch_checkbox = ttk.Checkbutton(patch_frame, text=f"{patch['Name']} - {patch['Size']}", variable=patch_var)
    patch_checkbox.pack(anchor="w")
    patch_var.trace_add("write", lambda *args: check_addon_selection(patch_db_url, download_button_patches))
    patch["var"] = patch_var

download_button_addon = ttk.Button(window, text="Download Addons", command=download_addons)
download_button_addon["state"] = "disabled"
download_button_addon.pack(side="bottom", pady=(0, 15))
download_button_addon.place(in_=addon_frame, relx=0.5, rely=1.20, anchor="s")

download_button_patches = ttk.Button(window, text="Download Patches", command=download_patches)
download_button_patches["state"] = "disabled"
download_button_patches.pack(side="bottom", pady=(0, 15))
download_button_patches.place(in_=patch_frame, relx=0.5, rely=1.68, anchor="s")

loading_animation = ttk.Progressbar(window, mode="indeterminate")

window.mainloop()