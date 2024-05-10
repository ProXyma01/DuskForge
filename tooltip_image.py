import os
import sys
from PIL import Image
import customtkinter as cus

def load_images(num_images):
    images = []
    if getattr(sys, 'frozen', False): 
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath(__file__)) 

    for i in range(1, num_images + 1):
        image_path = os.path.join(bundle_dir, 'source', f'image{i}.jpg')
        img = cus.CTkImage(Image.open(image_path), size=(400, 400))
        images.append(img)
    return images

num_images = 22
images = load_images(num_images)
