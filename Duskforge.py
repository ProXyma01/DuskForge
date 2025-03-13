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
    chosen_location = CONF.get("default_location", "")
    if chosen_location:
        check_detection_button.configure(state="normal")  
    else:
        check_detection_button.configure(state="disabled")  


def choose_default_location():
    wow_folder_path = filedialog.askdirectory()
    if not wow_folder_path or isinstance(wow_folder_path, tuple):
        check_detection_button.configure(state="disabled")
        return
    
    current_position = window.geometry()
    
    default = os.path.join(wow_folder_path)
    default_location = os.path.join(wow_folder_path, "Interface", "Addons")
    default_location_patches = os.path.join(wow_folder_path, "Data")
    
    CONF.update({
        "default_location_patches": default_location_patches,
        "default_location": default_location,
        "default": default,
        "window_position": current_position 
    })
    
    if os.path.exists(core_utils_instance.config_file):
        os.remove(core_utils_instance.config_file)
    
    core_utils_instance.save_config(CONF)
    update_check_detection_button_state()


def msg_box_lang_change():
    chosen_location = CONF.get("default_location_patches", "")
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
        

def center_window(window, width, height):

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    center_x = (screen_width - width) // 2
    center_y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{center_x}+{center_y}")

def save_window_position(window):
    CONF["window_position"] = window.geometry()
    core_utils_instance.save_config(CONF)

def restore_window_position(window):
    if "window_position" in CONF:
        window.geometry(CONF["window_position"])
    else:
        center_window(window, width=1000, height=900)



CONF = core_utils_instance.load_config()
window = cus.CTk()
window.title("Duskforge (by R00T)")
cus.set_appearance_mode("dark")
window_width = 1000
window_height = 900
restore_window_position(window)
window.protocol("WM_DELETE_WINDOW", lambda: [save_window_position(window), window.destroy()])
window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=1)

def realmlist_updater(server):
    wow_folder = CONF.get("default", "")
    if not wow_folder:
        CTkMessagebox(title="Error",message="WoW folder location not set!", icon="cancel")
        return

    realmlist_path = os.path.join(wow_folder, "Data", "enUS", "realmlist.wtf")
    if not os.path.exists(realmlist_path):
        CTkMessagebox(title="Error",message=f"realmlist.wtf not found at:\n{realmlist_path}",icon="cancel")
        return

    server_addresses = {
        "Warmane": "logon.warmane.com",
        "Warsong": "logon.warsong.ge"
    }

    try:
        if not os.access(realmlist_path, os.W_OK):
            CTkMessagebox(title="Error",message=f"No write permission for:\n{realmlist_path}\nRun the app as Administrator.",icon="cancel")
            return

        with open(realmlist_path, "w") as file:
            file.write(f"set realmlist {server_addresses[server]}\n")
        CTkMessagebox(title="Success",message=f"Updated realmlist.wtf to:\n{server_addresses[server]}",icon="check")
    
    except Exception as e:
        CTkMessagebox(title="Error",message=f"Failed to update realmlist.wtf:\n{e}",icon="cancel")

def combobox_callback(choice):
    realmlist_updater(choice)
    
    CONF["selected_server"] = choice 
    try:
        core_utils_instance.save_config(CONF)  
    except Exception as e:
        CTkMessagebox(title="Error",message=f"Failed to save config:\n{e}",icon="cancel")

combo_box = cus.CTkComboBox(
    master=window,
    state="readonly",
    values=["Warsong", "Warmane"],  
    command=combobox_callback,
    fg_color="#242424",  
    button_color="#242424",  
    border_color="#242424",
    button_hover_color="#1c1b1b",
    dropdown_fg_color="#242424",  
    dropdown_text_color="#f7f5ed",
    dropdown_font=("Arial", 12),  
    width=150, 
    height=30  
)
combo_box.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
if "selected_server" in CONF:
    combo_box.set(CONF["selected_server"]) 
else:
    combo_box.set("404")



check_detection_button = cus.CTkButton(master=window)
detection_window = DetectionWindow(CONF, check_detection_button)
check_detection_button.configure(text="Check Downloads", command=detection_window.update_detection_window,
        width=170, height=45, fg_color="#0a4a0c", hover_color="#0c6e0f", font=("cursive", 18))
check_detection_button.grid(row=0, column=0, pady=10)


update_check_detection_button_state()

tabview = cus.CTkTabview(master=window, fg_color="#242424")
tabview.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

# Addon TAB

addons_tab = tabview.add("Addons")
addons_tab.grid_columnconfigure(0, weight=1)  
addons_tab.grid_columnconfigure(1, weight=1)  

addon_frame_left = cus.CTkFrame(master=addons_tab, fg_color="#242424", height=600)
addon_frame_left.grid(row=0, column=0, padx=(10, 50), pady=10, sticky="nw")
addon_frame_right = cus.CTkFrame(master=addons_tab, fg_color="#242424", height=600)
addon_frame_right.grid(row=0, column=1, padx=(50, 10), pady=10, sticky="ne")

midpoint = len(addon_db_url) // 2
left_addons = addon_db_url[:midpoint]
right_addons = addon_db_url[midpoint:]

addon_vars = []
APP_BACKGROUND_COLOR = window.cget("bg")
addon_names = [addon["Name"] for addon in addon_db_url]
images = tooltip_image.load_images(addon_names, max_width=450, max_height=300)

for addon in left_addons:
    addon_var = tk.BooleanVar()
    addon_vars.append(addon_var)
    addon_checkbox = cus.CTkCheckBox(
        addon_frame_left, 
        fg_color="#0a4a0c", 
        hover_color="#0c6e0f", 
        text=addon["Name"], 
        text_color="#f7f5ed", 
        variable=addon_var
    )
    addon_checkbox.pack(anchor="w", pady=(0, 2))
    CTkToolTip(
        addon_checkbox,
        image=images.get(addon["Name"]),
        message="",
        delay=0.2,
        bg_color=APP_BACKGROUND_COLOR,
        border_color=APP_BACKGROUND_COLOR,
        corner_radius=0
    )
    addon_var.trace_add("write", lambda *args: check_addon_selection(addon_db_url, download_button_selected))
    addon["var"] = addon_var


for addon in right_addons:
    addon_var = tk.BooleanVar()
    addon_vars.append(addon_var)
    addon_checkbox = cus.CTkCheckBox(
        addon_frame_right, 
        fg_color="#0a4a0c", 
        hover_color="#0c6e0f", 
        text=addon["Name"], 
        text_color="#f7f5ed", 
        variable=addon_var
    )
    addon_checkbox.pack(anchor="w", pady=(0, 2))
    CTkToolTip(
        addon_checkbox,
        image=images.get(addon["Name"]),
        message="",
        delay=0.2,
        bg_color=APP_BACKGROUND_COLOR,
        border_color=APP_BACKGROUND_COLOR,
        corner_radius=0
    )
    addon_var.trace_add("write", lambda *args: check_addon_selection(addon_db_url, download_button_selected))
    addon["var"] = addon_var


# patches tab

patches_tab = tabview.add("Patches")
patches_tab.grid_columnconfigure(0, weight=1)
patches_tab.grid_columnconfigure(1, weight=1)

patch_frame = cus.CTkFrame(master=patches_tab, fg_color="#242424", height=600)
patch_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="n")

patch_vars = []
for i, patch in enumerate(patch_db_url):
    patch_var = tk.BooleanVar()
    patch_vars.append(patch_var)
    patch_checkbox = cus.CTkCheckBox(patch_frame, text_color="#f7f5ed", fg_color="#0a4a0c", hover_color="#0c6e0f", text=f"{patch['Name']} - {patch['Size']}", variable=patch_var)
    patch_checkbox.pack(anchor="w", pady=(0, 2))
    patch_var.trace_add("write", lambda *args: check_addon_selection(patch_db_url, download_button_selected))
    patch["var"] = patch_var




download_button_selected = cus.CTkButton(master=window, text="Download Selected", command=lambda: download_selected())
download_button_selected.configure(state="disabled", width=150, height=45, fg_color="#0a4a0c", hover_color="#0c6e0f", font=("cursive", 18))
download_button_selected.grid(row=3, column=0, pady=(20, 15))

default_location_button = cus.CTkButton(master=window, text="Choose WOW Folder Location", command=choose_default_location)
default_location_button.configure(width=200, height=50, fg_color="#0a4a0c", hover_color="#0c6e0f", font=("cursive", 18))
default_location_button.grid(row=4, column=0, pady=15)

language_button = cus.CTkButton(master=window, command=lambda: change_and_map_language())
language_button.configure(text="ENG", width=20, image=img_lang_en, fg_color="transparent", hover_color="#242424")
language_button.place(relx=1.0, rely=0.95, anchor="se", x=-4, y=38)


def change_and_map_language():
    lang_manager.change_language(language_button, download_button_selected, 
            default_location_button, check_detection_button, launch_wow_button)

def download_selected():
    loading_animation.grid(row=2, column=0, pady=(5, 10))
    chosen_location_addons = CONF.get("default_location", "")
    chosen_location_patches = CONF.get("default_location_patches", "")
    
    if not (chosen_location_addons and chosen_location_patches):
        loading_animation.grid_forget()
        if lang_manager.current_language == "en":
            CTkMessagebox(title="", message="Choose WoW folder Location", icon="warning", option_1="Ok")
        elif lang_manager.current_language == "ge":
            CTkMessagebox(title="", message="აირჩიე WOW ფოლდერის ლოკაცია", font=("Arial", 15), icon="warning", option_1="Ok")
        return

    downloaded_addons = []
    downloaded_patches = []

    def download_thread():
        loading_animation.start()
        
        for addon in addon_db_url:
            if addon.get("var") and addon["var"].get():
                addon_name = addon["Name"]
                addon_folder = os.path.join(chosen_location_addons)
                os.makedirs(addon_folder, exist_ok=True)
                addon_zip = os.path.join(addon_folder, addon_name + ".zip")
                success = down_addon(addon["Url"], addon_zip)
                if success:
                    success = extract_zip(addon_zip, addon_folder)
                    os.remove(addon_zip)
                addon["var"].set(False)
                if success:
                    downloaded_addons.append(addon_name)

        for patch in patch_db_url:
            if patch.get("var") and patch["var"].get():
                patch_name = patch["Name"]
                patch_url = patch["Url"]
                patch_file = os.path.join(chosen_location_patches, patch_name)
                success = down_patch(patch_url, patch_file)
                if success:
                    downloaded_patches.append(patch_name)
                patch["var"].set(False)

        window.after(0, show_result)

    def show_result():
        loading_animation.grid_forget()
        if lang_manager.current_language == "en":
            if downloaded_addons or downloaded_patches:
                addon_names = ', '.join(downloaded_addons) if downloaded_addons else ""
                patch_names = ', '.join(downloaded_patches) if downloaded_patches else ""
                message = f"Addons: {addon_names}\nPatches: {patch_names}".strip()
                CTkMessagebox(title="", message=f"Downloaded successfully!\n{message}", icon="check")
        elif lang_manager.current_language == "ge":
            if downloaded_addons or downloaded_patches:
                addon_names = ', '.join(downloaded_addons) if downloaded_addons else ""
                patch_names = ', '.join(downloaded_patches) if downloaded_patches else ""
                message = f"ადონები: {addon_names}\nპაჩები: {patch_names}".strip()
                CTkMessagebox(title="", message=f"გადმოწერა წარმატებით დასრულდა!\n{message}", font=("Arial", 15), icon="check")

    threading.Thread(target=download_thread).start()

def check_addon_selection(db, button):
    for item in db:
        if item.get("var") and item["var"].get():
            button.configure(state="normal")
            return
    button.configure(state="disabled")

lang_manager = LanguageManager(current_language="en")
core_utils_instance_sec = Core.Utils(lang_manager=lang_manager)

launch_wow_button = cus.CTkButton(master=window, text="Start The Game", command=core_utils_instance_sec.launch_wow)
launch_wow_button.configure(width=150, height=50, fg_color="#0a4a0c", hover_color="#0c6e0f", font=("cursive", 18))
launch_wow_button.grid(row=5, column=0, pady=10)

loading_animation = cus.CTkProgressBar(window, height=15, progress_color="#0a4a0c", mode="indeterminate")
window.mainloop()