import os
import sys
import json
import ctypes
import subprocess
from CTkMessagebox import CTkMessagebox

class Utils:
    def __init__(self, lang_manager):
        self.lang_manager = lang_manager
        self.config_file = "config.json"
        self.config = self.load_config()


    def load_addon_urls(self):
        bundle_dir = self.get_bundle_dir()
        addon_json_path = os.path.join(bundle_dir, 'json', 'addon_wotlk_db_url.json')
        with open(addon_json_path, 'r') as addon_file:
            return json.load(addon_file)

    def get_bundle_dir(self):
        if getattr(sys, 'frozen', False): 
            return sys._MEIPASS
        else:
            return os.path.dirname(os.path.abspath(__file__)) 

    def load_patch_urls(self):
        bundle_dir = self.get_bundle_dir()
        patch_json_path = os.path.join(bundle_dir, 'json', 'patch_wotlk_db_url.json')
        with open(patch_json_path, 'r') as patch_file:
            return json.load(patch_file)
        
    def save_config(self, config):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as file:
                json.dump(config, file)
            FILE_ATTRIBUTE_HIDDEN = 0x02

            ctypes.windll.kernel32.SetFileAttributesW(self.config_file, FILE_ATTRIBUTE_HIDDEN)
        except PermissionError as e:
            CTkMessagebox(title="", message=f"Error saving configuration: {e}",  icon="cancel", 
                option_1="Ok")
        except Exception as e:
            CTkMessagebox(title="", message=f"An error occurred while saving configuration: {e}",  icon="cancel", 
                option_1="Ok")

    def load_config(self):
        CONFIG_FILE = "config.json"
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    def launch_wow(self):
        choose_location = self.config.get("default")
        if not choose_location:
            if self.lang_manager.current_language == "en":
                CTkMessagebox(title="", message="Choose WoW folder Location",  icon="warning", 
                            option_1="Ok")
            elif self.lang_manager.current_language == "ge":
                CTkMessagebox(title="", message="აირჩიე WOW ფოლდერის ლოკაცია", font=("Arial", 15), icon="warning", 
                            option_1="Ok")
        else:
            wow_path =  os.path.join(choose_location, "Wow.exe")
            if os.path.exists(wow_path):
                subprocess.Popen(wow_path)
            else:
                if self.lang_manager.current_language == "en":
                    CTkMessagebox(title="", message="File Wow.exe not found!",  icon="cancel", 
                            option_1="Ok")
                elif  self.lang_manager.current_language == "ge":
                    CTkMessagebox(title="", message="ფაილი Wow.exe არ არსებობს!",  icon="cancel", 
                            option_1="Ok")
