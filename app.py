import customtkinter as ctk
from pages.youtubepage import YouTubePage
from pages.tiktokpage import TikTokPage
from pages.linkgrabberpage import LinkGrabberPage
from utils import resource_path

# ============================================
# Design Tokens / Theme Configuration
# ============================================
COLORS = {
    # Primary colors
    "primary": "#3b82f6",
    "primary_hover": "#2563eb",
    "primary_dark": "#1d4ed8",
    
    # Status colors
    "success": "#22c55e",
    "success_hover": "#16a34a",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "error_hover": "#dc2626",
    
    # Background colors (Dark theme)
    "bg_primary": "#0f172a",
    "bg_secondary": "#1e293b",
    "bg_tertiary": "#334155",
    "bg_card": "#1e293b",
    
    # Text colors
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    
    # Border colors
    "border": "#334155",
    "border_light": "#475569",
    
    # Tab colors
    "tab_active": "#3b82f6",
    "tab_inactive": "transparent",
}

FONTS = {
    "heading": ("Segoe UI", 18, "bold"),
    "subheading": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 12),
    "small": ("Segoe UI", 10),
    "tiny": ("Segoe UI", 9),
    "button": ("Segoe UI", 12, "bold"),
    "tab": ("Segoe UI", 13, "bold"),
    "console": ("Consolas", 10),
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- Window Configuration ---
        self.geometry("900x650")
        self.minsize(800, 600)
        self.title("VortexDev Tool | Video Downloader V2.0")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        try:
            self.iconbitmap(resource_path("logotean.ico"))
        except:
            pass
        
        # Configure main window background
        self.configure(fg_color=COLORS["bg_primary"])
        
        # --- Main Container with Card Effect ---
        self.main_container = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_secondary"],
            corner_radius=20,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # --- Create Header ---
        self.create_header()
        
        # --- Create Tab Navigation ---
        self.create_tab_navigation()
        
        # --- Main Content Frame for Pages ---
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        self.content_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # --- Create and Store Page Instances ---
        self.pages = {
            "youtube": YouTubePage(self.content_frame),
            "tiktok": TikTokPage(self.content_frame),
            "linkgrabber": LinkGrabberPage(self.content_frame)
        }
        
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")
        
        # --- Create Footer ---
        self.create_footer()
        
        # --- Show default page ---
        self.select_page("youtube")

    def create_header(self):
        """Creates the premium header with logo and controls."""
        header_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent",
            height=60
        )
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        header_frame.pack_propagate(False)
        
        # Left side - Logo and Title
        left_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="y")
        
        # Logo icon (gradient effect simulated with colored frame)
        logo_frame = ctk.CTkFrame(
            left_frame,
            width=40,
            height=40,
            corner_radius=10,
            fg_color=COLORS["primary"]
        )
        logo_frame.pack(side="left", padx=(0, 10))
        logo_frame.pack_propagate(False)
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="▶",
            font=("Segoe UI", 18),
            text_color="white"
        )
        logo_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title text
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="y", pady=5)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="VortexDev Tool",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        )
        title_label.pack(anchor="w")
        
        version_label = ctk.CTkLabel(
            title_frame,
            text="Video Downloader V2.0",
            font=FONTS["tiny"],
            text_color=COLORS["text_muted"]
        )
        version_label.pack(anchor="w")
        
        # Right side - Controls
        right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="y")
        
        # Theme toggle button
        self.theme_btn = ctk.CTkButton(
            right_frame,
            text="🌙",
            width=40,
            height=40,
            corner_radius=10,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["border_light"],
            font=("Segoe UI", 16),
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="left", padx=(0, 10))
        
        # Status indicators
        status_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        status_frame.pack(side="left", pady=10)
        
        for color in [COLORS["success"], COLORS["warning"], COLORS["error"]]:
            dot = ctk.CTkFrame(
                status_frame,
                width=10,
                height=10,
                corner_radius=5,
                fg_color=color
            )
            dot.pack(side="left", padx=2)

    def create_tab_navigation(self):
        """Creates the premium tab navigation bar."""
        tab_container = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS["bg_tertiary"],
            corner_radius=12,
            height=50
        )
        tab_container.pack(fill="x", padx=15, pady=(0, 10))
        tab_container.pack_propagate(False)
        
        # Inner frame for tabs
        inner_frame = ctk.CTkFrame(tab_container, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=4, pady=4)
        inner_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # YouTube Tab
        self.youtube_tab = ctk.CTkButton(
            inner_frame,
            text="▶  YOUTUBE",
            font=FONTS["tab"],
            height=38,
            corner_radius=10,
            fg_color=COLORS["bg_secondary"],
            hover_color=COLORS["bg_secondary"],
            text_color=COLORS["primary"],
            command=lambda: self.select_page("youtube")
        )
        self.youtube_tab.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        # TikTok Tab
        self.tiktok_tab = ctk.CTkButton(
            inner_frame,
            text="♪  TIKTOK",
            font=FONTS["tab"],
            height=38,
            corner_radius=10,
            fg_color="transparent",
            hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"],
            command=lambda: self.select_page("tiktok")
        )
        self.tiktok_tab.grid(row=0, column=1, sticky="ew", padx=2)
        
        # Link Grabber Tab
        self.linkgrabber_tab = ctk.CTkButton(
            inner_frame,
            text="🔗  LINK GRABBER",
            font=FONTS["tab"],
            height=38,
            corner_radius=10,
            fg_color="transparent",
            hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"],
            command=lambda: self.select_page("linkgrabber")
        )
        self.linkgrabber_tab.grid(row=0, column=2, sticky="ew", padx=(2, 0))

    def create_footer(self):
        """Creates the footer with copyright."""
        footer_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS["bg_tertiary"],
            height=35,
            corner_radius=0
        )
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        footer_label = ctk.CTkLabel(
            footer_frame,
            text="© 2024 VortexDev Software Solutions. All rights reserved.",
            font=FONTS["tiny"],
            text_color=COLORS["text_muted"]
        )
        footer_label.pack(expand=True)

    def select_page(self, page_name):
        """Handles tab selection and page switching."""
        # Reset all tabs to inactive state
        tabs = {
            "youtube": self.youtube_tab,
            "tiktok": self.tiktok_tab,
            "linkgrabber": self.linkgrabber_tab
        }
        
        for name, tab in tabs.items():
            if name == page_name:
                tab.configure(
                    fg_color=COLORS["bg_secondary"],
                    text_color=COLORS["primary"]
                )
            else:
                tab.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"]
                )
        
        # Show selected page
        self.pages[page_name].tkraise()

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="☀️")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="🌙")


# --- Main Execution ---
if __name__ == "__main__":
    app = App()
    app.mainloop()
