import os
import customtkinter as cus
from CTkMessagebox import CTkMessagebox

class DetectionWindow:
    def __init__(self, config, check_detection_button):
        self.config = config
        self.det_win = None
        self.label_button_map = {}
        self.no_patches_label = None
        self.button_states = {}
        self.check_detection_button = check_detection_button

    def delete_patch(self, file_name):
        try:
            if file_name.startswith("PATCH-") or file_name.startswith("~"):
                os.remove(os.path.join(self.config.get("default_location_patches"), file_name))
                self.update_detection_window()
        except Exception as e:
            CTkMessagebox(title="", message=f"Failed to delete {file_name}: {e}", icon="cancel", option_1="Ok")
    
    def toggle_patch(self, patch_name, com_btn):
        current_path = os.path.join(self.config.get("default_location_patches"), patch_name)
        new_path = os.path.join(self.config.get("default_location_patches"), "~" + patch_name)
        if os.path.exists(current_path):
            os.rename(current_path, new_path)
            com_btn.configure(text="Resume", fg_color="green")
        else:
            os.rename(new_path, current_path)
            com_btn.configure(text="Pause", fg_color="red")
        self.update_detection_window()

    
    def comment_patch(self, patch_name, comment_button):
        if patch_name[0] == "~":
            self.toggle_patch(patch_name[1:], comment_button)
        else:
            self.toggle_patch(patch_name, comment_button)

    def update_detection_window(self):
        
        if self.det_win is None or not self.det_win.winfo_exists():
            self.det_win = cus.CTkToplevel()
            self.det_win.title("Delete Patches")
            self.det_win.resizable(False, False)
            self.det_win.grab_set()

        chosen_location = self.config.get("default_location", "")
        if chosen_location:
            downloaded_patches = []
            patch_directory = self.config.get("default_location_patches")
            if os.path.exists(patch_directory) and os.path.isdir(patch_directory):
                downloaded_patches = [patch for patch in os.listdir(patch_directory) if
                                    (patch.startswith("PATCH-") or patch.startswith("~PATCH-")) and patch.endswith(".MPQ")]
            self.show_patch_det_win(downloaded_patches)
        else:
            CTkMessagebox(title="", message="Location Not found, Relaunch Program.", icon="cancel", option_1="Ok")

    def show_patch_det_win(self, patch_names):
        
        def toggle_patch_button_text(p_name):
            if p_name[0] != "~":
                return "Pause"
            else:
                return "Resume"        
   
        def toggle_patch_btn_color(p_color):
            if p_color[0] != "~":
                return "#0a4a0c"
            else:
                return "#d6180b"

        for widget in self.det_win.winfo_children():
            widget.destroy()

        self.det_win.grid_rowconfigure(0, weight=1)
        self.det_win.grid_columnconfigure(0, weight=1)
        self.det_win.grid_columnconfigure(1, weight=1)
        self.det_win.grid_columnconfigure(2, weight=1)
        
        if not patch_names:
            self.no_patches_label = cus.CTkLabel(self.det_win, text="No patches are installed", font=("Arial", 20))
            self.no_patches_label.pack(pady=35)
        else:
            for i, patch_name in enumerate(patch_names):
                label = cus.CTkLabel(self.det_win, text=patch_name, font=("Arial", 18))
                label.grid(row=i+1, column=0, padx=10, pady=3, sticky="ew")

                delete_button = cus.CTkButton(self.det_win, text="X", font=("Arial", 18, "bold"), command=lambda p=patch_name: self.delete_patch(p))
                delete_button.configure(width=25, fg_color="#d6180b", hover_color="#fc1000")
                delete_button.grid(row=i+1, column=1, padx=10, pady=3, sticky="ew")

                comment_button = cus.CTkButton(self.det_win, text=toggle_patch_button_text(patch_name), fg_color="#0a4a0c", hover_color="#0c6e0f")
                comment_button.grid(row=i+1, column=2, padx=10, pady=3, sticky="ew")
                comment_button.configure(command=lambda p=patch_name, b=comment_button: self.comment_patch(p, b), fg_color=toggle_patch_btn_color(patch_name))
        
        required_height = (len(patch_names)) * 35 
        min_height = 100 
        window_height = max(required_height, min_height)
        self.det_win.geometry(f"400x{window_height}") 
