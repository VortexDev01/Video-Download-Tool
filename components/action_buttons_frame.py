import customtkinter as ctk

# Design tokens
COLORS = {
    "primary": "#3b82f6",
    "primary_hover": "#2563eb",
    "success": "#22c55e",
    "success_hover": "#16a34a",
    "error": "#ef4444",
    "error_hover": "#dc2626",
    "bg_tertiary": "#334155",
    "border": "#475569",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
}

FONTS = {
    "button_primary": ("Segoe UI", 13, "bold"),
    "button": ("Segoe UI", 11, "bold"),
}


class ActionButtonsFrame(ctk.CTkFrame):
    """Premium action buttons with gradient-like primary button and styled secondary buttons."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        
        # Grid layout for buttons
        self.grid_columnconfigure(0, weight=2)  # Download button takes more space
        self.grid_columnconfigure((1, 2, 3), weight=1)
        
        # --- Download Now Button (Primary) ---
        self.download_btn = ctk.CTkButton(
            self,
            text="⬇  DOWNLOAD NOW",
            font=FONTS["button_primary"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="white",
            corner_radius=10,
            height=45,
            command=controller.start_download
        )
        self.download_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        # --- Stop Button (Danger outline) ---
        self.cancel_btn = ctk.CTkButton(
            self,
            text="⬛ Stop",
            font=FONTS["button"],
            fg_color="transparent",
            hover_color="#3f1f1f",
            text_color=COLORS["error"],
            border_width=1,
            border_color=COLORS["error"],
            corner_radius=10,
            height=45,
            state="disabled",
            command=controller.cancel_download
        )
        self.cancel_btn.grid(row=0, column=1, sticky="ew", padx=4)
        
        # --- Load Folder Button (Success outline) ---
        self.load_folder_btn = ctk.CTkButton(
            self,
            text="📁 Load Folder",
            font=FONTS["button"],
            fg_color="transparent",
            hover_color="#1f3f2f",
            text_color=COLORS["success"],
            border_width=1,
            border_color=COLORS["success"],
            corner_radius=10,
            height=45,
            command=controller.choose_folder
        )
        self.load_folder_btn.grid(row=0, column=2, sticky="ew", padx=4)
        
        # --- Open Folder Button (Secondary) ---
        self.open_folder_btn = ctk.CTkButton(
            self,
            text="📂 Open Folder",
            font=FONTS["button"],
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=10,
            height=45,
            command=controller.open_folder
        )
        self.open_folder_btn.grid(row=0, column=3, sticky="ew", padx=(4, 0))
    
    def set_state_downloading(self):
        """Set UI state when download is in progress."""
        self.download_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
    
    def set_state_idle(self):
        """Set UI state when idle (not downloading)."""
        self.download_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")
