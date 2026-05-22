import customtkinter as ctk
from tkinter import filedialog
import os

# Import components
from components.url_input_frame import UrlInputFrame
from components.options_frame import OptionsFrame
from components.action_buttons_frame import ActionButtonsFrame
from components.status_frame import StatusFrame
from services.youtube import DownloaderService


class YouTubePage(ctk.CTkFrame):
    """YouTube download page with premium UI design."""
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # --- Initialize Attributes ---
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
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # --- Form Card Container ---
        self.form_card = ctk.CTkFrame(
            self,
            fg_color="#1e293b",
            corner_radius=12,
            border_width=1,
            border_color="#334155"
        )
        self.form_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.form_card.grid_columnconfigure(0, weight=1)
        
        # --- URL Input ---
        self.url_input_frame = UrlInputFrame(self.form_card)
        self.url_input_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 15))
        
        # --- Options Frame ---
        self.options_frame = OptionsFrame(self.form_card, controller=self)
        self.options_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # --- Action Buttons ---
        self.actions_frame = ActionButtonsFrame(self.form_card, controller=self)
        self.actions_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # --- Status Frame (Progress + Logs) ---
        self.status_frame = StatusFrame(self)
        self.status_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 0))
        
        # --- Initialize UI ---
        self.status_frame.update_folder_label(self.download_dir)
        self.log("Application started. Ready to download.")

    def start_download(self):
        """Start the download process."""
        url = self.url_input_frame.get_url()
        if not url:
            self.log("❌ Please enter a valid URL")
            return
        
        self.log("🚀 Starting download process...")
        self.video_count = 0
        self.status_frame.update_counter_label(self.video_count)
        self.status_frame.start_progress()
        self.actions_frame.set_state_downloading()
        
        options = self.options_frame.get_options()
        options['download_dir'] = self.download_dir
        
        self.downloader.start_download(url, options)
    
    def cancel_download(self):
        """Cancel the current download."""
        self.downloader.cancel_download()
        self.log("⚠️ Download cancelled by user")
        
    def choose_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory(initialdir=self.download_dir)
        if folder:
            self.download_dir = folder
            self.status_frame.update_folder_label(self.download_dir)
            self.log(f"📁 Download location changed to: {folder}")
    
    def open_folder(self):
        """Open the download folder in file explorer."""
        os.makedirs(self.download_dir, exist_ok=True)
        try:
            os.startfile(self.download_dir)
        except AttributeError:
            try:
                os.system(f'open "{self.download_dir}"')
            except:
                os.system(f'xdg-open "{self.download_dir}"')
    
    def check_total_videos(self):
        """Check the total number of videos in playlist/channel."""
        url = self.url_input_frame.get_url()
        if not url:
            self.log("❌ Please enter a valid URL")
            return
        
        self.log("🔍 Checking total video count...")
        self.actions_frame.set_state_downloading()
        self.options_frame.update_total_label("Total videos: checking...")
        
        options = self.options_frame.get_options()
        self.downloader.start_count_check(url, options)
    
    def log(self, message):
        """Add a message to the activity log."""
        self.status_frame.log(message)
    
    def increment_video_count(self):
        """Increment and display the video counter."""
        self.video_count += 1
        self.status_frame.update_counter_label(self.video_count)
    
    def update_total_label(self, text):
        """Update the total videos label."""
        self.options_frame.update_total_label(text)
    
    def on_download_complete(self):
        """Handle download completion."""
        self.status_frame.stop_progress()
        self.actions_frame.set_state_idle()
        self.log("✅ Download complete!")

    def on_count_complete(self):
        """Handle count check completion."""
        self.actions_frame.set_state_idle()

