import os
import tkinter as tk
import shutil
import threading
import gdown
from tkinter import filedialog, ttk
from zipfile import ZipFile
from requests.exceptions import Timeout
import requests
from CTkMessagebox import CTkMessagebox
import customtkinter as cus
from Det_win import DetectionWindow
from Lang_manager import LanguageManager, img_lang_en
import Core
from CTkToolTip import *
import tooltip_image


core_utils_instance = Core.Utils(lang_manager=None)  ### for Importing all methods except launch_wow

addon_db_url = core_utils_instance.load_addon_urls()
patch_db_url = core_utils_instance.load_patch_urls() 


def down_addon(url, filename, timeout=30):
    try:
        with requests.get(url, stream=True, timeout=timeout) as req:
            dl = 0
            block_size = 1024

            with open(filename, 'wb') as file:
                for data in req.iter_content(block_size):
                    dl += len(data)
                    file.write(data)

        return True
    except Timeout:
        CTkMessagebox(title="", message=f"Request Time out, Check Your Internet Connection", icon="cancel")
        return False
    except Exception as e:
        CTkMessagebox(title="", message=f"Double-Check Your Chosen Location \nTry Choosing It again", icon="cancel")
        return False


def down_patch(url, filename):
    try:
        print(f"Downloading Started, Don't Close this window.")
        gdown.download(url, filename, quiet=True)
        print(f"Download of {filename} completed successfully!")
        return True
    except Exception as e:
        CTkMessagebox(title="", message=f"Double-Check Your Chosen Location \nTry Choosing It again", icon="cancel")
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
        CTkMessagebox(title="", message=f"An error occurred: {e}", icon="cancel")
        return False


def update_check_detection_button_state():
    chosen_location = config.get("default_location", "")
    if chosen_location:
        check_detection_button.configure(state="normal")  
    else:
        check_detection_button.configure(state="disabled")  


def choose_default_location():
    wow_folder_path = filedialog.askdirectory()
    if not wow_folder_path or isinstance(wow_folder_path, tuple):
        check_detection_button.configure(state="disabled")
    
    default = os.path.join(wow_folder_path)
    default_location = os.path.join(wow_folder_path, "Interface", "Addons")
    default_location_patches = os.path.join(wow_folder_path, "Data")
    config["default_location_patches"] = default_location_patches
    config["default_location"] = default_location
    config["default"] = default
    
    if os.path.exists(core_utils_instance.config_file):
        os.remove(core_utils_instance.config_file)
    
    core_utils_instance.save_config(config)
    update_check_detection_button_state()


def msg_box_lang_change():
    chosen_location = config.get("default_location_patches", "")
    if not chosen_location:
            loading_animation.pack_forget()
            if lang_manager.current_language == "en":
                CTkMessagebox(title="", message="Choose WoW folder Location", icon="warning",
                            option_1="Ok")
            elif lang_manager.current_language == "ge":
                CTkMessagebox(title="", message="აირჩიე WOW ფოლდერის ლოკაცია", font=("Arial", 15), icon="warning", 
                            option_1="Ok")
            return False
    
    else: return True
        

def download_patches():
    loading_animation.pack(side="bottom", pady=(0,10))
    chosen_location = config.get("default_location_patches", "")
    if msg_box_lang_change():

        downloaded_patches = []
        def down_p(patch):
            loading_animation.start()   
            patch_name = patch["Name"]
            patch_url = patch["Url"]
            patch_file = os.path.join(chosen_location, patch_name)
            success = down_patch(patch_url, patch_file)

            if success:
                downloaded_patches.append(patch_name)
            
        def download_thread():
            for patch in patch_db_url:
                if patch.get("var") is not None and patch["var"].get():
                    down_p(patch)
                    patch["var"].set(False)

            window.after(0, show_patch_result)

        def show_patch_result():
            loading_animation.pack_forget()
            if lang_manager.current_language == "en":
                if downloaded_patches:
                    patch_names = ', '.join(downloaded_patches)
                    CTkMessagebox(title="", message=f"Patches '{patch_names}' were Downloaded and installed successfully!", icon="check",
                                option_1="Ok")
            elif lang_manager.current_language == "ge":
                if downloaded_patches:
                    patch_names = ', '.join(downloaded_patches)
                    CTkMessagebox(title="", message=f"პაჩები '{patch_names}' გადმოწერა და დაყენდა წარმატებით!", font=("Arial", 15), icon="check",
                                option_1="Ok")

        threading.Thread(target=download_thread).start()


def check_addon_selection(db, button):
    for addon in db:
        if addon["var"].get():
            button.configure(state="normal")
            return
    button.configure(state="disabled")


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    center_x = (screen_width - width) // 2
    center_y = (screen_height - height) // 2

    window.geometry(f"{width}x{height+100}+{center_x}+{center_y}")


def download_addons():
    loading_animation.pack(side="bottom", pady=(0,10))
    chosen_location = config.get("default_location", "")
    
    if msg_box_lang_change():
        downloaded_addons = []

        def download_thread():
            loading_animation.start()
            for addon in addon_db_url:
                if addon.get("var").get():
                    addon_name = addon["Name"]
                    addon_folder = os.path.join(chosen_location)
                    os.makedirs(addon_folder, exist_ok=True)
                    addon_zip = os.path.join(addon_folder, addon_name + ".zip")
                    success = down_addon(addon["Url"], addon_zip)

                    if success:
                        success = extract_zip(addon_zip, addon_folder)
                        os.remove(addon_zip)
                        
                    addon["var"].set(False)
                    if success:
                        downloaded_addons.append(addon_name)

            window.after(0, show_result)

        def show_result():
            loading_animation.pack_forget()

            if lang_manager.current_language == "en":
                if downloaded_addons:
                    addon_names = ', '.join(downloaded_addons)
                    CTkMessagebox(title="", message=f"Addons '{addon_names}' were Downloaded and Installed successfully!", icon="check")
            elif lang_manager.current_language == "ge":
                if downloaded_addons:
                    addon_names = ', '.join(downloaded_addons)
                    CTkMessagebox(title="", message=f"ადონები '{addon_names}' გადმოიწერა და დაყენდა წარმატებით!", font=("Arial", 15), icon="check")
                
        threading.Thread(target=download_thread).start()


config = core_utils_instance.load_config()
window = cus.CTk()
window.title("Duskforge (by R00T)")
cus.set_appearance_mode("dark")
center_window(window, 1000, 850) 
style = ttk.Style()
style.configure("TFrame", background="#ececec")
style.configure("TButton", background="#3f51b5", foreground="black", font=("Arial", 12, "bold"), padding=10)
style.map("TButton", background=[("active", "#5677fc")])
style.configure("TLabel", background="#ececec", font=("Arial", 12))
style.configure("TCheckbutton", background="#ececec", font=("Arial", 12))

default_location_button = cus.CTkButton(master=window, text="Choose WOW Folder Location", command=choose_default_location)
default_location_button.pack(padx=20, pady=20) 
default_location_button.configure(width=200, height=50, fg_color="#0a4a0c", hover_color="#0c6e0f", font=("cursive", 18))
default_location_button.pack(side="bottom", pady=15)

lang_manager = LanguageManager(current_language="en")  
core_utils_instance_sec = Core.Utils(lang_manager=lang_manager) ### for Importhing launch_wow method

launch_wow_button = cus.CTkButton(master=window, text="Start The Game", command=core_utils_instance_sec.launch_wow)
launch_wow_button.configure(width=150, height=50, fg_color="#0a4a0c", hover_color="#0c6e0f", font=("cursive", 18))
launch_wow_button.pack(side="bottom", pady=10)

check_detection_button = cus.CTkButton(master=window)
detection_window = DetectionWindow(config, check_detection_button)
check_detection_button = cus.CTkButton(master=window,)
update_check_detection_button_state() ### update Check_detection button without dynamically without reopening app

check_detection_button.configure(text="Check Downloads", command=detection_window.update_detection_window,
        width=170, height=45, fg_color="#0a4a0c", hover_color="#0c6e0f", font=("cursive", 18))
check_detection_button.pack(side="top", padx=10, pady=10)

addon_frame = cus.CTkFrame(master=window, fg_color="#242424")
addon_frame.place(relx=0, rely=0, anchor="nw")
addon_frame.place_configure(x=50, y=30)
cus.CTkLabel(addon_frame, text="Addons", width=200, text_color="#f7f5ed", font=("Arial", 20, "bold")).pack(pady=10)
ttk.Separator(addon_frame, orient="horizontal").pack(fill="x", padx=10, pady=(0, 10))

addon_vars = []
images = tooltip_image.load_images(num_images=22) 

for i, addon in enumerate(addon_db_url):
    addon_var = tk.BooleanVar()
    addon_vars.append(addon_var)
    addon_checkbox = cus.CTkCheckBox(addon_frame, fg_color="#0a4a0c", hover_color="#0c6e0f", text=addon["Name"], text_color="#f7f5ed", variable=addon_var)
    addon_checkbox.pack(anchor="w", pady=(0, 2))
    CTkToolTip(addon_checkbox, image=images[i], message="", delay=0.2)
    addon_var.trace_add("write", lambda *args: check_addon_selection(addon_db_url, download_button_addon))
    addon["var"] = addon_var


patch_frame = cus.CTkFrame(master=window, fg_color="#242424")
patch_frame.place(relx=1, rely=0, anchor="ne")
patch_frame.place_configure(x=-50, y=30)

cus.CTkLabel(patch_frame, text="Patches", width=200, font=("Arial", 14, "bold")).pack(pady=10)
ttk.Separator(patch_frame, orient="horizontal").pack(fill="x", padx=10, pady=(0, 10))


patch_vars = []
for i, patch in enumerate(patch_db_url):
    patch_var = tk.BooleanVar()
    patch_vars.append(patch_var)
    patch_checkbox =  cus.CTkCheckBox(patch_frame, text_color="#f7f5ed", fg_color="#0a4a0c", hover_color="#0c6e0f", text=f"{patch['Name']} - {patch['Size']}", variable=patch_var)
    patch_checkbox.pack(anchor="w", pady=(0, 2))
    patch_var.trace_add("write", lambda *args: check_addon_selection(patch_db_url, download_button_patches))
    patch["var"] = patch_var


download_button_addon =  cus.CTkButton(master=window, text="Download Addons", command=download_addons)
download_button_addon.configure(state="disabled",  width=150, height=45, 
    fg_color="#0a4a0c", hover_color="#0c6e0f", font=("cursive", 18))
download_button_addon.pack(side="bottom", pady=(0, 15))
download_button_addon.place(in_=addon_frame, relx=0.5, rely=1.171, anchor="s")

download_button_patches = cus.CTkButton(master=window, text="Download Patches", command=download_patches)
download_button_patches.configure(state="disabled", width=150, height=45, 
    fg_color="#0a4a0c", hover_color="#0c6e0f", font=("cursive", 18))

download_button_patches.pack(side="bottom", pady=(0, 15))
download_button_patches.place(in_=patch_frame, relx=0.5, rely=1.639, anchor="s")


def change_and_map_language():
    lang_manager.change_language(language_button, download_button_addon, download_button_patches, 
                                 default_location_button, check_detection_button, launch_wow_button)

language_button = cus.CTkButton(master=window, command=change_and_map_language)
language_button.configure(text="ENG", width=20, image=img_lang_en, fg_color="transparent", hover_color="#242424")
language_button.place(relx=1.0, rely=0.95, anchor="se", x=-4, y=38)

loading_animation = cus.CTkProgressBar(window, height=15, progress_color="#0a4a0c", mode="indeterminate")

window.mainloop()

