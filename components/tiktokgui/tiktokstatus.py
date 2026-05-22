import customtkinter as ctk
from datetime import datetime
import re

# Design tokens
COLORS = {
    "bg_log": "#0f172a",
    "bg_log_header": "#1a2744",
    "bg_tertiary": "#334155",
    "border": "#334155",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "primary": "#3b82f6",
    "success": "#4ade80",
    "warning": "#facc15",
    "error": "#f87171",
    "info": "#38bdf8",
}

FONTS = {
    "label": ("Segoe UI", 11),
    "small": ("Segoe UI", 10),
    "tiny": ("Segoe UI", 9),
    "console": ("Consolas", 10),
    "console_header": ("Segoe UI", 9, "bold"),
}


class TiktokStatus(ctk.CTkFrame):
    """Premium status frame for TikTok with folder label, progress bar, activity log, and counter."""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # --- Save Location Label ---
        self.folder_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_tertiary"],
            corner_radius=8,
            height=35
        )
        self.folder_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.folder_frame.grid_propagate(False)
        
        folder_icon = ctk.CTkLabel(
            self.folder_frame,
            text="📁",
            font=("Segoe UI", 12)
        )
        folder_icon.pack(side="left", padx=(12, 5), pady=5)
        
        self.folder_label = ctk.CTkLabel(
            self.folder_frame,
            text="Save to: ",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        self.folder_label.pack(side="left", pady=5)
        
        # --- Progress Section ---
        progress_header = ctk.CTkFrame(self, fg_color="transparent")
        progress_header.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        
        progress_label = ctk.CTkLabel(
            progress_header,
            text="Current Progress",
            font=FONTS["label"],
            text_color=COLORS["text_secondary"]
        )
        progress_label.pack(side="left")
        
        self.progress_percent = ctk.CTkLabel(
            progress_header,
            text="0%",
            font=FONTS["label"],
            text_color=COLORS["primary"]
        )
        self.progress_percent.pack(side="right")
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(
            self,
            mode='determinate',
            height=8,
            corner_radius=4,
            fg_color=COLORS["bg_tertiary"],
            progress_color=COLORS["primary"]
        )
        self.progress.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        self.progress.set(0)
        
        # --- Activity Log (Console-style) ---
        self.log_container = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_log"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.log_container.grid(row=3, column=0, sticky="nsew", pady=(0, 0))
        self.log_container.grid_rowconfigure(1, weight=1)
        self.log_container.grid_columnconfigure(0, weight=1)
        
        # Log header
        log_header = ctk.CTkFrame(
            self.log_container,
            fg_color=COLORS["bg_log_header"],
            corner_radius=0,
            height=32
        )
        log_header.grid(row=0, column=0, sticky="ew")
        log_header.grid_propagate(False)
        
        # Pulse dot and ACTIVITY LOG text
        header_content = ctk.CTkFrame(log_header, fg_color="transparent")
        header_content.pack(side="left", padx=12, pady=6)
        
        self.pulse_dot = ctk.CTkFrame(
            header_content,
            width=8,
            height=8,
            corner_radius=4,
            fg_color=COLORS["success"]
        )
        self.pulse_dot.pack(side="left", padx=(0, 8))
        
        log_title = ctk.CTkLabel(
            header_content,
            text="ACTIVITY LOG",
            font=FONTS["console_header"],
            text_color=COLORS["text_secondary"]
        )
        log_title.pack(side="left")
        
        # Log textbox
        self.logs_text = ctk.CTkTextbox(
            self.log_container,
            font=FONTS["console"],
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            state="disabled",
            wrap="word",
            corner_radius=0
        )
        self.logs_text.grid(row=1, column=0, sticky="nsew", padx=12, pady=(8, 0))
        
        # Configure text tags for colored output
        self.logs_text._textbox.tag_configure("time", foreground=COLORS["text_muted"])
        self.logs_text._textbox.tag_configure("info", foreground=COLORS["info"])
        self.logs_text._textbox.tag_configure("success", foreground=COLORS["success"])
        self.logs_text._textbox.tag_configure("warning", foreground=COLORS["warning"])
        self.logs_text._textbox.tag_configure("error", foreground=COLORS["error"])
        
        # Log footer
        log_footer = ctk.CTkFrame(
            self.log_container,
            fg_color=COLORS["bg_log_header"],
            corner_radius=0,
            height=28
        )
        log_footer.grid(row=2, column=0, sticky="ew")
        log_footer.grid_propagate(False)
        
        # System status
        status_frame = ctk.CTkFrame(log_footer, fg_color="transparent")
        status_frame.pack(side="left", padx=12, pady=5)
        
        status_dot = ctk.CTkFrame(
            status_frame,
            width=6,
            height=6,
            corner_radius=3,
            fg_color=COLORS["success"]
        )
        status_dot.pack(side="left", padx=(0, 6))
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="SYSTEM OK",
            font=FONTS["tiny"],
            text_color=COLORS["text_muted"]
        )
        status_label.pack(side="left")
        
        # Video counter
        self.counter_label = ctk.CTkLabel(
            log_footer,
            text="Count_video: 0",
            font=FONTS["tiny"],
            text_color=COLORS["text_muted"]
        )
        self.counter_label.pack(side="right", padx=12, pady=5)
    
    def log(self, message, log_type="info"):
        """Add a log entry with timestamp and color coding."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Strip ANSI escape codes from the message
        ansi_pattern = re.compile(r'\x1b\[[0-9;]*m|\[0;?[0-9]*m\]?')
        clean_message = ansi_pattern.sub('', message)
        
        self.logs_text.configure(state="normal")
        
        # Insert timestamp
        self.logs_text._textbox.insert("end", f"[{timestamp}] ", "time")
        
        # Determine message type from content
        if "❌" in clean_message or "error" in clean_message.lower():
            tag = "error"
        elif "✅" in clean_message or "success" in clean_message.lower() or "complete" in clean_message.lower():
            tag = "success"
        elif "⚠️" in clean_message or "warning" in clean_message.lower() or "Downloading:" in clean_message:
            tag = "warning"
        else:
            tag = "info"
        
        # Insert message with appropriate color
        self.logs_text._textbox.insert("end", f"{clean_message}\n", tag)
        
        self.logs_text.see("end")
        self.logs_text.configure(state="disabled")
    
    def update_folder_label(self, path):
        """Update the save location display."""
        self.folder_label.configure(text=f"Save to: {path}")
    
    def update_counter_label(self, count):
        """Update the video counter."""
        self.counter_label.configure(text=f"Count_video: {count}")
    
    def update_total_label(self, text):
        """Update total label - compatibility method."""
        pass  # Not used in TikTok status
    
    def update_progress(self, value):
        """Update progress bar (0.0 to 1.0)."""
        self.progress.set(value)
        self.progress_percent.configure(text=f"{int(value * 100)}%")
    
    def start_progress(self):
        """Start indeterminate progress animation."""
        self.progress.configure(mode='indeterminate')
        self.progress.start()
        self.progress_percent.configure(text="...")
    
    def stop_progress(self):
        """Stop progress animation and reset."""
        self.progress.stop()
        self.progress.configure(mode='determinate')
        self.progress.set(0)
        self.progress_percent.configure(text="0%")
