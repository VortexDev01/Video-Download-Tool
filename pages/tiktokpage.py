import customtkinter as ctk
from tkinter import filedialog
import os

# Import TikTok-specific components
from components.tiktokgui.url_input import UrlInput
from components.tiktokgui.button_frame import ButtonFrame
from components.tiktokgui.optionmenu import OptionMenu
from components.tiktokgui.tiktokstatus import TiktokStatus
from services.tiktok import DownloadService


class TikTokPage(ctk.CTkFrame):
    """TikTok download page with premium UI design."""
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # --- Initialize Attributes ---
        self.limit_var = ctk.StringVar(value="0")
        self.quality_var = ctk.StringVar(value="1080p")
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
        self.downloader = DownloadService(callbacks)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
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
        self.url_input_frame = UrlInput(self.form_card)
        self.url_input_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 15))
        
        # --- Options Frame ---
        self.optionMenu_frame = OptionMenu(self.form_card, controller=self)
        self.optionMenu_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # --- Action Buttons ---
        self.action_buttons_frame = ButtonFrame(self.form_card, controller=self)
        self.action_buttons_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # --- Status Frame (Progress + Logs) ---
        self.status_tiktok_frame = TiktokStatus(self)
        self.status_tiktok_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 0))
        
        # --- Initialize UI ---
        self.status_tiktok_frame.update_folder_label(self.download_dir)
        self.log("Application started. Ready to download.")

    def tiktok_start_download(self):
        """Start the TikTok download process."""
        url = self.url_input_frame.get_url()
        if not url:
            self.log("❌ Please enter a valid URL")
            return
        
        self.log("🚀 Starting download process...")
        self.video_count = 0
        self.status_tiktok_frame.update_counter_label(self.video_count)
        self.status_tiktok_frame.start_progress()
        self.action_buttons_frame.set_state_downloading()
        
        options = self.optionMenu_frame.get_options()
        options['download_dir'] = self.download_dir
        
        self.downloader.tiktok_start_download(url, options)
    
    def tiktok_cancel_download(self):
        """Cancel the current download."""
        self.downloader.tiktok_cancel_download()
        self.log("⚠️ Download cancelled by user")

    def tiktok_choose_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory(initialdir=self.download_dir)
        if folder:
            self.download_dir = folder
            self.status_tiktok_frame.update_folder_label(self.download_dir)
            self.log(f"📁 Download location changed to: {folder}")

    def tiktok_open_folder(self):
        """Open the download folder in file explorer."""
        os.makedirs(self.download_dir, exist_ok=True)
        try:
            os.startfile(self.download_dir)
        except AttributeError:
            try:
                os.system(f'open "{self.download_dir}"')
            except:
                os.system(f'xdg-open "{self.download_dir}"')

    def log(self, message):
        """Add a message to the activity log."""
        self.status_tiktok_frame.log(message)
    
    def increment_video_count(self):
        """Increment and display the video counter."""
        self.video_count += 1
        self.status_tiktok_frame.update_counter_label(self.video_count)
    
    def update_total_label(self, total):
        """Update the total videos label."""
        self.optionMenu_frame.update_total_label(total)

    def on_download_complete(self):
        """Handle download completion."""
        self.status_tiktok_frame.stop_progress()
        self.action_buttons_frame.set_state_idle()
        self.log("✅ Download complete!")

    def on_count_complete(self):
        """Handle count check completion."""
        self.action_buttons_frame.set_state_idle()