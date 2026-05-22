# app.py
import tkinter as tk
from tkinter import filedialog
import os
from services.youtube import DownloaderService
from components.header import Header
from components.url_input_frame import UrlInputFrame
from components.options_frame import OptionsFrame
from components.action_buttons_frame import ActionButtonsFrame
from components.status_frame import StatusFrame

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tool VortexDev - Youtube Downloader")
        self.geometry("900x680")
        self.resizable(False, False)
        
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        self.video_count = 0

        # Create service with callbacks
        callbacks = {
            'log': self.log,
            'update_counter': self.increment_video_count,
            'update_total': self.update_total_label,
            'on_complete': self.on_download_complete,
            'on_count_complete': self.on_count_complete
        }
        
        self.downloader = DownloaderService(callbacks)

        # Create and layout components
        Header(self).pack(fill=tk.X)
        
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.url_frame = UrlInputFrame(main_frame)
        self.url_frame.pack(fill=tk.X, pady=(10,0))
        
        self.options_frame = OptionsFrame(main_frame, controller=self)
        self.options_frame.pack(fill=tk.X, pady=10)
        
        self.actions_frame = ActionButtonsFrame(main_frame, controller=self)
        self.actions_frame.pack(fill=tk.X, pady=5)
        
        self.status_frame = StatusFrame(main_frame)
        self.status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.status_frame.update_folder_label(self.download_dir)

    # --- Controller Methods (called by components) ---
    def start_download(self):
        url = self.url_frame.get_url()
        if not url:
            self.log("❌ Please enter a valid URL")
            return
        
        self.log("🚀 Starting download process...")
        self.video_count = 0 # Reset counter
        self.status_frame.update_counter_label(self.video_count)
        self.status_frame.start_progress()
        self.actions_frame.set_state_downloading()
        
        options = self.options_frame.get_options()
        options['download_dir'] = self.download_dir
        self.downloader.start_download(url, options)

    def cancel_download(self):
        self.downloader.cancel_download()

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_dir)
        if folder:
            self.download_dir = folder
            self.status_frame.update_folder_label(self.download_dir)
            self.log(f"📁 Download location changed to: {folder}")
            
    def open_folder(self):
        os.makedirs(self.download_dir, exist_ok=True)
        try: os.startfile(self.download_dir)
        except AttributeError:
            try: os.system(f'open "{self.download_dir}"')
            except: os.system(f'xdg-open "{self.download_dir}"')

    def check_total_videos(self):
        url = self.url_frame.get_url()
        if not url:
            self.log("❌ Please enter a URL to check")
            return
        self.log("🔎 Checking total number of videos...")
        self.actions_frame.set_state_downloading() # Reuse this state to disable buttons
        self.options_frame.update_total_label("Total videos: checking…")
        options = self.options_frame.get_options()
        self.downloader.start_count_check(url, options)

    # --- Callback Methods (called by service) ---
    def log(self, message):
        self.status_frame.log(message)

    def increment_video_count(self):
        self.video_count += 1
        self.status_frame.update_counter_label(self.video_count)

    def update_total_label(self, text):
        self.options_frame.update_total_label(text)
        
    def on_download_complete(self):
        self.status_frame.stop_progress()
        self.actions_frame.set_state_idle()

    def on_count_complete(self):
        self.actions_frame.set_state_idle()

if __name__ == "__main__":
    app = App()
    app.mainloop()