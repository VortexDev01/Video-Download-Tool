import customtkinter as ctk
import os
from tkinter import filedialog

# Design tokens
COLORS = {
    "bg_tertiary": "#334155",
    "bg_input": "#1e293b",
    "border": "#475569",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "primary": "#3b82f6",
}

FONTS = {
    "label": ("Segoe UI", 9, "bold"),
    "input": ("Segoe UI", 11),
    "button": ("Segoe UI", 11, "bold"),
}


class OptionsFrame(ctk.CTkFrame):
    """Simple options frame with quality, limit, type selectors and check count button."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        
        self.controller = controller
        self.quality_var = ctk.StringVar(value="best")
        self.limit_var = ctk.StringVar(value="0")
        self.type_var = ctk.StringVar(value="All videos")
        
        # Grid layout for options (4 columns)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # --- Quality Option ---
        quality_frame = self._create_option_group(self, "QUALITY", 0)
        self.quality_menu = ctk.CTkOptionMenu(
            quality_frame,
            variable=self.quality_var,
            values=["best", "1080p", "720p", "480p", "360p", "worst"],
            font=FONTS["input"],
            fg_color=COLORS["bg_tertiary"],
            button_color=COLORS["bg_tertiary"],
            button_hover_color=COLORS["border"],
            dropdown_fg_color=COLORS["bg_input"],
            dropdown_hover_color=COLORS["bg_tertiary"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            height=38
        )
        self.quality_menu.pack(fill="x")
        
        # --- Limit Option ---
        limit_frame = self._create_option_group(self, "LIMIT (0=ALL)", 1)
        self.limit_entry = ctk.CTkEntry(
            limit_frame,
            textvariable=self.limit_var,
            font=FONTS["input"],
            fg_color=COLORS["bg_tertiary"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            height=38,
            justify="center"
        )
        self.limit_entry.pack(fill="x")
        
        # --- Type Option ---
        type_frame = self._create_option_group(self, "TYPE", 2)
        self.type_menu = ctk.CTkOptionMenu(
            type_frame,
            variable=self.type_var,
            values=["All videos", "Streams", "Long videos", "Short videos"],
            font=FONTS["input"],
            fg_color=COLORS["bg_tertiary"],
            button_color=COLORS["bg_tertiary"],
            button_hover_color=COLORS["border"],
            dropdown_fg_color=COLORS["bg_input"],
            dropdown_hover_color=COLORS["bg_tertiary"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            height=38
        )
        self.type_menu.pack(fill="x")
        
        # --- Check Count Button ---
        check_frame = ctk.CTkFrame(self, fg_color="transparent")
        check_frame.grid(row=0, column=3, sticky="ew", padx=(10, 0))
        
        # Spacer label to align with other options
        spacer = ctk.CTkLabel(check_frame, text="", height=20)
        spacer.pack()
        
        self.check_btn = ctk.CTkButton(
            check_frame,
            text="🔍 Check Count",
            font=FONTS["button"],
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            height=38,
            border_width=1,
            border_color=COLORS["border"],
            command=controller.check_total_videos
        )
        self.check_btn.pack(fill="x")
        
        # --- Total Label (row 1) ---
        self.total_label = ctk.CTkLabel(
            self,
            text="Total videos: —",
            font=FONTS["input"],
            text_color=COLORS["text_muted"]
        )
        self.total_label.grid(row=1, column=0, columnspan=4, sticky="e", pady=(10, 0))
    
    def _create_option_group(self, parent, label_text, column):
        """Helper to create a labeled option group."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 10, 0))
        
        label = ctk.CTkLabel(
            frame,
            text=label_text,
            font=FONTS["label"],
            text_color=COLORS["text_muted"]
        )
        label.pack(anchor="w", pady=(0, 6))
        
        return frame
    
    def get_options(self):
        """Get current option values."""
        try:
            limit = int(self.limit_var.get())
        except ValueError:
            limit = 0
        
        return {
            'quality': self.quality_var.get(),
            'limit': limit if limit > 0 else None,
            'type': self.type_var.get()
        }
    
    def update_total_label(self, text):
        """Update the total videos label."""
        self.total_label.configure(text=text)
