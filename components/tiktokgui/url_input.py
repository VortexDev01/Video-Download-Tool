import customtkinter as ctk

# Design tokens
COLORS = {
    "bg_tertiary": "#334155",
    "bg_input": "#1e293b",
    "border": "#475569",
    "border_focus": "#3b82f6",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
}

FONTS = {
    "label": ("Segoe UI", 11),
    "input": ("Segoe UI", 12),
}


class UrlInput(ctk.CTkFrame):
    """Premium URL input component for TikTok with icon and styling."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.url_var = ctk.StringVar()
        
        # Label
        label = ctk.CTkLabel(
            self,
            text="TikTok Account / Video URL",
            font=FONTS["label"],
            text_color=COLORS["text_secondary"]
        )
        label.pack(anchor="w", pady=(0, 8))
        
        # Input container with icon
        input_container = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_tertiary"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        input_container.pack(fill="x")
        
        # TikTok icon
        icon_label = ctk.CTkLabel(
            input_container,
            text="♪",
            font=("Segoe UI", 16),
            text_color=COLORS["text_muted"],
            width=40
        )
        icon_label.pack(side="left", padx=(10, 0))
        
        # URL Entry
        self.url_entry = ctk.CTkEntry(
            input_container,
            textvariable=self.url_var,
            font=FONTS["input"],
            placeholder_text="Paste TikTok URL here...",
            placeholder_text_color=COLORS["text_muted"],
            text_color=COLORS["text_primary"],
            fg_color="transparent",
            border_width=0,
            height=45
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(5, 15), pady=2)
        
        # Focus effects
        self.url_entry.bind("<FocusIn>", lambda e: input_container.configure(border_color=COLORS["border_focus"]))
        self.url_entry.bind("<FocusOut>", lambda e: input_container.configure(border_color=COLORS["border"]))
    
    def get_url(self):
        return self.url_var.get().strip()
    
    def clear(self):
        self.url_var.set("")