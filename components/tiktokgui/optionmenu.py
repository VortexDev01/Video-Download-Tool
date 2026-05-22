import customtkinter as ctk

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


class OptionMenu(ctk.CTkFrame):
    """Premium options frame for TikTok with quality and limit selectors."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        
        self.quality_var = ctk.StringVar(value="best")
        self.limit_var = ctk.StringVar(value="0")
        
        # Grid layout for options
        self.grid_columnconfigure((0, 1), weight=1)
        
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
        
        # --- Total Label (below options) ---
        self.total_label = ctk.CTkLabel(
            self,
            text="Total videos: —",
            font=FONTS["input"],
            text_color=COLORS["text_muted"]
        )
        self.total_label.grid(row=1, column=0, columnspan=2, sticky="e", pady=(10, 0))
    
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
        try:
            limit = int(self.limit_var.get())
        except ValueError:
            limit = 0
        
        return {
            'quality': self.quality_var.get(),
            'limit': limit if limit > 0 else None,
        }
    
    def update_total_label(self, text):
        self.total_label.configure(text=text)
