import os
import sys
from PIL import Image
import customtkinter as cus

if getattr(sys, 'frozen', False): 
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__)) 

path_ico_ge = os.path.join(bundle_dir, 'source', 'lang_geo.ico')
path_ico_en = os.path.join(bundle_dir, 'source', 'lang_en.ico')

img_lang_en = cus.CTkImage(Image.open(path_ico_en), size=(30, 20))
img_lang_geo = cus.CTkImage(Image.open(path_ico_ge), size=(30, 20))


class LanguageManager:
    def __init__(self, current_language):
        self.current_language = current_language

    def change_language(self, language_button, download_button_selected, 
                        default_location_button, check_detection_button, launch_wow_button):
        if self.current_language == "ge":
            self.current_language = "en"
            language_button.configure(image=img_lang_en, text="ENG")
            download_button_selected.configure(text="Download Selected", width=150, height=45, font=("cursive", 18))
            default_location_button.configure(text="Choose Default Location", width=200, height=50, font=("cursive", 18))
            check_detection_button.configure(text="Check Downloads", width=170, height=45, font=("cursive", 18))
            launch_wow_button.configure(text="Start The Game", width=150, height=50, font=("cursive", 18))
        else:
            self.current_language = "ge"
            language_button.configure(image=img_lang_geo, text="GEO")
            download_button_selected.configure(text="გადმოწერე არჩეული", width=150, height=45, font=("Arial", 20, 'bold'))
            default_location_button.configure(text="აირჩიე WOW ფოლდერის ლოკაცია", width=200, height=50, font=("Arial", 20, 'bold'))
            check_detection_button.configure(text="შეამოწმე გადმოწერილები", width=170, height=45, font=("Arial", 20, 'bold'))
            launch_wow_button.configure(text="დაიწყე თამაში", width=150, height=50, font=("Arial", 20, 'bold'))