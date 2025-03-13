import os
import sys
from PIL import Image, ImageOps
import customtkinter as cus

APP_BACKGROUND_COLOR = "#242424"  

def load_images(addon_names, max_width=400, max_height=400):

    images = {}
    if getattr(sys, 'frozen', False): 
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    for i, addon_name in enumerate(addon_names):
        try:
            image_path = os.path.join(bundle_dir, 'source', f'image{i+1}.jpg')
            img = Image.open(image_path)
            
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            delta_width = max_width - img.size[0]
            delta_height = max_height - img.size[1]
            padding = (
                delta_width // 2,
                delta_height // 2,
                delta_width - (delta_width // 2),
                delta_height - (delta_height // 2)
            )
            
            img = ImageOps.expand(img, padding, fill=APP_BACKGROUND_COLOR)
            
            ctk_img = cus.CTkImage(img, size=(max_width, max_height))
            images[addon_name] = ctk_img
        except Exception as e:
            print(f"Error loading image for {addon_name}: {e}")
            placeholder = Image.new('RGB', (max_width, max_height), color=APP_BACKGROUND_COLOR)
            images[addon_name] = cus.CTkImage(placeholder, size=(max_width, max_height))
    
    return images