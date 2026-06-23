import customtkinter as ctk
from tkinter import filedialog
import re
import os
import threading
from urllib.parse import urlparse
from collections import defaultdict
from yt_dlp import YoutubeDL
from datetime import datetime
from services.ydl_utils import apply_runtime_options, is_tiktok_url, is_youtube_url

# ============================================
# Design Tokens
# ============================================
COLORS = {
    "bg_primary": "#0f172a",
    "bg_secondary": "#1e293b",
    "bg_tertiary": "#334155",
    "bg_card": "#1e293b",
    "bg_input": "#0f172a",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "border": "#334155",
    "border_light": "#475569",
    "border_focus": "#3b82f6",
    "primary": "#3b82f6",
    "primary_hover": "#2563eb",
    "success": "#22c55e",
    "success_hover": "#16a34a",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "error_hover": "#dc2626",
}

FONTS = {
    "heading": ("Segoe UI", 16, "bold"),
    "subheading": ("Segoe UI", 13, "bold"),
    "body": ("Segoe UI", 11),
    "small": ("Segoe UI", 10),
    "tiny": ("Segoe UI", 9),
    "label": ("Segoe UI", 9, "bold"),
    "mono": ("Consolas", 10),
    "console": ("Consolas", 9),
}


class LinkGrabberPage(ctk.CTkFrame):
    """Link Grabber page - Paste multiple URLs and manage them for download."""
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # --- Data Storage ---
        self.all_links = []
        self.filtered_links = []
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        self.is_downloading = False
        self.cancel_event = threading.Event()
        self.current_download_index = 0
        self.total_to_download = 0
        self.completed_count = 0
        self.failed_count = 0
        
        # --- Filter States ---
        self.hide_duplicates = ctk.BooleanVar(value=True)
        self.hide_blocked = ctk.BooleanVar(value=True)
        self.hide_same_origin = ctk.BooleanVar(value=False)
        self.group_by_domain = ctk.BooleanVar(value=False)
        self.filter_text = ctk.StringVar()
        
        # --- Download Options ---
        self.quality_var = ctk.StringVar(value="best")
        self.limit_var = ctk.StringVar(value="0")
        
        # Blocked domains
        self.blocked_domains = {'ads.', 'tracking.', 'analytics.'}
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        
        # --- Create UI Components ---
        self._create_input_section()
        self._create_options_section()
        self._create_filter_bar()
        self._create_main_content()
        self._create_status_bar()
        
        # Initial log
        self.log("🔗 Link Grabber ready. Paste URLs and click 'Parse URLs'.")
    
    def _create_input_section(self):
        """Creates the multi-line URL input section."""
        input_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        input_card.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        
        # Header row
        header_row = ctk.CTkFrame(input_card, fg_color="transparent")
        header_row.pack(fill="x", padx=15, pady=(10, 5))
        
        input_label = ctk.CTkLabel(
            header_row,
            text="🔗 Paste URLs (one per line)",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        input_label.pack(side="left")
        
        # Text Area Frame
        text_frame = ctk.CTkFrame(
            input_card,
            fg_color=COLORS["bg_input"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"]
        )
        text_frame.pack(fill="x", padx=15, pady=(0, 8))
        
        self.url_textbox = ctk.CTkTextbox(
            text_frame,
            height=70,
            font=FONTS["mono"],
            fg_color="transparent",
            text_color=COLORS["text_primary"],
            border_width=0,
            wrap="none"
        )
        self.url_textbox.pack(fill="x", padx=5, pady=5)
        
        # Buttons row
        btn_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.parse_btn = ctk.CTkButton(
            btn_frame,
            text="📥 Parse URLs",
            font=FONTS["body"],
            height=32,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._parse_urls
        )
        self.parse_btn.pack(side="left", padx=(0, 8))
        
        self.paste_btn = ctk.CTkButton(
            btn_frame,
            text="📋 Paste",
            font=FONTS["body"],
            height=32,
            corner_radius=8,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["border_light"],
            command=self._paste_from_clipboard
        )
        self.paste_btn.pack(side="left", padx=(0, 8))
        
        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear",
            font=FONTS["body"],
            height=32,
            corner_radius=8,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["error"],
            command=self._clear_all
        )
        self.clear_btn.pack(side="left")
    
    def _create_options_section(self):
        """Creates the download options section."""
        options_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        options_card.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        
        inner_frame = ctk.CTkFrame(options_card, fg_color="transparent")
        inner_frame.pack(fill="x", padx=15, pady=10)
        inner_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # --- Quality Option ---
        quality_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        quality_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        ctk.CTkLabel(
            quality_frame, text="QUALITY", font=FONTS["label"],
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.quality_menu = ctk.CTkOptionMenu(
            quality_frame,
            variable=self.quality_var,
            values=["best", "1080p", "720p", "480p", "360p", "worst"],
            font=FONTS["body"],
            fg_color=COLORS["bg_tertiary"],
            button_color=COLORS["bg_tertiary"],
            button_hover_color=COLORS["border"],
            dropdown_fg_color=COLORS["bg_input"],
            dropdown_hover_color=COLORS["bg_tertiary"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            height=34
        )
        self.quality_menu.pack(fill="x")
        
        # --- Limit Option ---
        limit_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        limit_frame.grid(row=0, column=1, sticky="ew", padx=10)
        
        ctk.CTkLabel(
            limit_frame, text="LIMIT (0=ALL)", font=FONTS["label"],
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.limit_entry = ctk.CTkEntry(
            limit_frame,
            textvariable=self.limit_var,
            font=FONTS["body"],
            fg_color=COLORS["bg_tertiary"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
            corner_radius=8,
            height=34,
            justify="center"
        )
        self.limit_entry.pack(fill="x")
        
        # --- Download Button ---
        download_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        download_frame.grid(row=0, column=2, sticky="ew", padx=10)
        
        ctk.CTkLabel(download_frame, text="", height=16).pack()
        
        self.download_btn = ctk.CTkButton(
            download_frame,
            text="⬇️ Download",
            font=("Segoe UI", 11, "bold"),
            height=34,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color=COLORS["success_hover"],
            command=self._start_download
        )
        self.download_btn.pack(fill="x")
        
        # --- Stop Button ---
        stop_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        stop_frame.grid(row=0, column=3, sticky="ew", padx=10)
        
        ctk.CTkLabel(stop_frame, text="", height=16).pack()
        
        self.stop_btn = ctk.CTkButton(
            stop_frame,
            text="⏹️ Stop",
            font=("Segoe UI", 11, "bold"),
            height=34,
            corner_radius=8,
            fg_color=COLORS["error"],
            hover_color=COLORS["error_hover"],
            state="disabled",
            command=self._stop_download
        )
        self.stop_btn.pack(fill="x")
        
        # --- Folder Buttons ---
        folder_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
        folder_frame.grid(row=0, column=4, sticky="ew", padx=(10, 0))
        
        ctk.CTkLabel(folder_frame, text="FOLDER", font=FONTS["label"],
                     text_color=COLORS["text_muted"]).pack(anchor="w", pady=(0, 4))
        
        folder_btn_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        folder_btn_frame.pack(fill="x")
        
        self.load_folder_btn = ctk.CTkButton(
            folder_btn_frame,
            text="📂 Load",
            font=FONTS["small"],
            width=60,
            height=34,
            corner_radius=8,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["border_light"],
            command=self._choose_folder
        )
        self.load_folder_btn.pack(side="left", padx=(0, 5))
        
        self.open_folder_btn = ctk.CTkButton(
            folder_btn_frame,
            text="📁 Open",
            font=FONTS["small"],
            width=60,
            height=34,
            corner_radius=8,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["border_light"],
            command=self._open_folder
        )
        self.open_folder_btn.pack(side="left")
    
    def _create_filter_bar(self):
        """Creates the filter options bar."""
        filter_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
            height=40
        )
        filter_card.grid(row=2, column=0, sticky="new", pady=(0, 5))
        filter_card.grid_propagate(False)
        
        inner_frame = ctk.CTkFrame(filter_card, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=12, pady=6)
        
        # Checkboxes
        for text, var in [
            ("Hide duplicates", self.hide_duplicates),
            ("Hide blocked", self.hide_blocked),
            ("Hide same origin", self.hide_same_origin),
            ("Group by domain", self.group_by_domain),
        ]:
            cb = ctk.CTkCheckBox(
                inner_frame, text=text, font=FONTS["small"],
                text_color=COLORS["text_secondary"], variable=var,
                checkbox_width=16, checkbox_height=16, corner_radius=4,
                fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                command=self._apply_filters
            )
            cb.pack(side="left", padx=(0, 12))
        
        # Search Entry
        filter_entry = ctk.CTkEntry(
            inner_frame,
            textvariable=self.filter_text,
            placeholder_text="filter...",
            font=FONTS["small"],
            height=24,
            width=100,
            corner_radius=6,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        filter_entry.pack(side="left", padx=(0, 12))
        filter_entry.bind("<KeyRelease>", lambda e: self._apply_filters())
        
        # Count label
        self.count_label = ctk.CTkLabel(
            inner_frame, text="0 / 0", font=FONTS["small"],
            text_color=COLORS["text_muted"]
        )
        self.count_label.pack(side="right")
        
        # Action buttons
        self.copy_btn = ctk.CTkButton(
            inner_frame, text="📋 Copy", font=FONTS["small"],
            height=24, width=60, corner_radius=6,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            command=self._copy_selected
        )
        self.copy_btn.pack(side="right", padx=(0, 10))
        
        self.deselect_btn = ctk.CTkButton(
            inner_frame, text="☐ None", font=FONTS["small"],
            height=24, width=60, corner_radius=6,
            fg_color=COLORS["bg_tertiary"], hover_color=COLORS["border_light"],
            command=self._deselect_all
        )
        self.deselect_btn.pack(side="right", padx=(0, 5))
        
        self.select_all_btn = ctk.CTkButton(
            inner_frame, text="☑️ All", font=FONTS["small"],
            height=24, width=60, corner_radius=6,
            fg_color=COLORS["bg_tertiary"], hover_color=COLORS["border_light"],
            command=self._select_all
        )
        self.select_all_btn.pack(side="right", padx=(0, 5))
    
    def _create_main_content(self):
        """Creates the main content area with links list and log."""
        # Main content container
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 5))
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # --- Links List (Left Side) ---
        list_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        list_card.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        list_card.grid_rowconfigure(0, weight=1)
        list_card.grid_columnconfigure(0, weight=1)
        
        self.links_scroll = ctk.CTkScrollableFrame(
            list_card, fg_color="transparent", corner_radius=0
        )
        self.links_scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.links_scroll.grid_columnconfigure(0, weight=1)
        
        self.placeholder_label = ctk.CTkLabel(
            self.links_scroll,
            text="📋 No links yet. Paste URLs and click 'Parse URLs'.",
            font=FONTS["body"],
            text_color=COLORS["text_muted"]
        )
        self.placeholder_label.grid(row=0, column=0, pady=30)
        
        # --- Activity Log (Right Side) ---
        log_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        log_card.grid(row=0, column=1, sticky="nsew")
        log_card.grid_rowconfigure(1, weight=1)
        log_card.grid_columnconfigure(0, weight=1)
        
        # Log header
        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 5))
        
        ctk.CTkLabel(
            log_header, text="📊 Activity Log", font=FONTS["subheading"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        # Counter label
        self.counter_label = ctk.CTkLabel(
            log_header, text="Downloaded: 0", font=FONTS["small"],
            text_color=COLORS["success"]
        )
        self.counter_label.pack(side="right")
        
        # Log textbox
        self.log_textbox = ctk.CTkTextbox(
            log_card,
            font=FONTS["console"],
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_secondary"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
            state="disabled"
        )
        self.log_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
    
    def _create_status_bar(self):
        """Creates the status bar."""
        status_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_secondary"],
            corner_radius=8,
            height=32
        )
        status_frame.grid(row=5, column=0, sticky="ew")
        status_frame.grid_propagate(False)
        
        inner = ctk.CTkFrame(status_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=5)
        
        self.folder_label = ctk.CTkLabel(
            inner,
            text=f"📁 {self.download_dir}",
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.folder_label.pack(side="left", fill="x", expand=True)
        
        self.progress_label = ctk.CTkLabel(
            inner, text="Ready", font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        self.progress_label.pack(side="right")
    
    # ============================================
    # Logging
    # ============================================
    
    def log(self, message):
        """Add message to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
    
    def update_counter(self):
        """Update the download counter."""
        self.completed_count += 1
        self.counter_label.configure(text=f"Downloaded: {self.completed_count}")
        self.progress_label.configure(
            text=f"Progress: {self.completed_count}/{self.total_to_download}"
        )
    
    # ============================================
    # URL Parsing
    # ============================================
    
    def _parse_urls(self):
        """Parse URLs from the text area."""
        text = self.url_textbox.get("1.0", "end-1c")
        lines = text.strip().split('\n')
        
        url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
        
        found_urls = []
        for line in lines:
            line = line.strip()
            if line:
                matches = url_pattern.findall(line)
                if matches:
                    found_urls.extend(matches)
                elif line.startswith(('http://', 'https://')):
                    found_urls.append(line)
        
        self.all_links = []
        for url in found_urls:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc
            except:
                domain = "unknown"
            
            self.all_links.append({
                'url': url,
                'domain': domain,
                'var': ctk.BooleanVar(value=True)
            })
        
        self._apply_filters()
        self.log(f"✅ Parsed {len(self.all_links)} URLs")
    
    def _paste_from_clipboard(self):
        """Paste content from clipboard."""
        try:
            clipboard_content = self.clipboard_get()
            self.url_textbox.delete("1.0", "end")
            self.url_textbox.insert("1.0", clipboard_content)
            self.log("📋 Pasted from clipboard")
        except:
            pass
    
    def _clear_all(self):
        """Clear all links."""
        self.url_textbox.delete("1.0", "end")
        self.all_links = []
        self.filtered_links = []
        self._render_links()
        self.log("🗑️ Cleared all links")
    
    # ============================================
    # Filtering
    # ============================================
    
    def _apply_filters(self):
        """Apply filters to the links list."""
        filtered = list(self.all_links)
        
        if self.hide_duplicates.get():
            seen = set()
            unique = []
            for link in filtered:
                if link['url'] not in seen:
                    seen.add(link['url'])
                    unique.append(link)
            filtered = unique
        
        if self.hide_blocked.get():
            filtered = [
                link for link in filtered
                if not any(blocked in link['domain'] for blocked in self.blocked_domains)
            ]
        
        if self.hide_same_origin.get():
            seen_domains = set()
            unique = []
            for link in filtered:
                if link['domain'] not in seen_domains:
                    seen_domains.add(link['domain'])
                    unique.append(link)
            filtered = unique
        
        filter_text = self.filter_text.get().strip().lower()
        if filter_text:
            filtered = [
                link for link in filtered
                if filter_text in link['url'].lower()
            ]
        
        if self.group_by_domain.get():
            grouped = defaultdict(list)
            for link in filtered:
                grouped[link['domain']].append(link)
            filtered = []
            for domain in sorted(grouped.keys()):
                filtered.extend(grouped[domain])
        
        self.filtered_links = filtered
        self._render_links()
    
    def _render_links(self):
        """Render the links list."""
        for widget in self.links_scroll.winfo_children():
            widget.destroy()
        
        if not self.filtered_links:
            self.placeholder_label = ctk.CTkLabel(
                self.links_scroll,
                text="📋 No links found.",
                font=FONTS["body"],
                text_color=COLORS["text_muted"]
            )
            self.placeholder_label.grid(row=0, column=0, pady=30)
            self._update_count_label()
            return
        
        current_domain = None
        row = 0
        
        for link in self.filtered_links:
            if self.group_by_domain.get() and link['domain'] != current_domain:
                current_domain = link['domain']
                domain_label = ctk.CTkLabel(
                    self.links_scroll,
                    text=f"🌐 {current_domain}",
                    font=FONTS["subheading"],
                    text_color=COLORS["primary"]
                )
                domain_label.grid(row=row, column=0, sticky="w", padx=10, pady=(8, 4))
                row += 1
            
            link_frame = ctk.CTkFrame(
                self.links_scroll,
                fg_color=COLORS["bg_tertiary"],
                corner_radius=6,
                height=28
            )
            link_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=1)
            link_frame.grid_columnconfigure(1, weight=1)
            
            checkbox = ctk.CTkCheckBox(
                link_frame, text="", variable=link['var'],
                checkbox_width=16, checkbox_height=16, corner_radius=4,
                fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                command=self._update_count_label
            )
            checkbox.grid(row=0, column=0, padx=(6, 4), pady=4)
            
            url_label = ctk.CTkLabel(
                link_frame,
                text=link['url'],
                font=FONTS["mono"],
                text_color=COLORS["text_primary"],
                anchor="w"
            )
            url_label.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=4)
            
            row += 1
        
        self._update_count_label()
    
    def _update_count_label(self):
        """Update the count label."""
        total = len(self.filtered_links)
        selected = sum(1 for link in self.filtered_links if link['var'].get())
        self.count_label.configure(text=f"{selected} / {total}")
    
    def _select_all(self):
        for link in self.filtered_links:
            link['var'].set(True)
        self._update_count_label()
    
    def _deselect_all(self):
        for link in self.filtered_links:
            link['var'].set(False)
        self._update_count_label()
    
    def _copy_selected(self):
        """Copy selected URLs to clipboard."""
        selected_urls = [link['url'] for link in self.filtered_links if link['var'].get()]
        if selected_urls:
            self.clipboard_clear()
            self.clipboard_append('\n'.join(selected_urls))
            self.log(f"📋 Copied {len(selected_urls)} URLs")
    
    # ============================================
    # Folder Management
    # ============================================
    
    def _choose_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory(initialdir=self.download_dir)
        if folder:
            self.download_dir = folder
            self.folder_label.configure(text=f"📁 {self.download_dir}")
            self.log(f"📂 Folder changed: {folder}")
    
    def _open_folder(self):
        """Open download folder."""
        os.makedirs(self.download_dir, exist_ok=True)
        try:
            os.startfile(self.download_dir)
        except AttributeError:
            try:
                os.system(f'open "{self.download_dir}"')
            except:
                os.system(f'xdg-open "{self.download_dir}"')
    
    # ============================================
    # Download Logic (Using yt-dlp)
    # ============================================
    
    def _quality_to_format(self, quality):
        """Convert quality setting to yt-dlp format."""
        formats = {
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
            "worst": "worst",
        }
        return formats.get(quality, "bestvideo+bestaudio/best")
    
    def _progress_hook(self, d):
        """yt-dlp progress hook."""
        if self.cancel_event.is_set():
            raise Exception("USER_CANCELLED")
        
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A').strip()
            self.after(0, lambda: self.progress_label.configure(
                text=f"⬇️ {percent} @ {speed}"
            ))
        
        elif d['status'] == 'finished':
            filename = os.path.basename(d.get('filename', 'Unknown'))
            self.after(0, lambda fn=filename: self.log(f"✓ Downloaded: {fn}"))
            self.after(0, self.update_counter)
    
    def _count_partial_files(self):
        """Count leftover partial files in the active download folder."""
        partial_count = 0
        for root, _, files in os.walk(self.download_dir):
            for name in files:
                if name.endswith((".part", ".ytdl")):
                    partial_count += 1
        return partial_count

    def _build_ydl_opts(self):
        """Build yt-dlp options tuned for pasted social/video links."""
        ydl_opts = {
            'format': self._quality_to_format(self.quality_var.get()),
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s').replace('\\', '/'),
            'progress_hooks': [self._progress_hook],
            'ignoreerrors': False,
            # Fresh downloads are safer for signed media URLs from sites like YouTube/TikTok
            'continuedl': False,
            'retries': 5,
            'fragment_retries': 5,
            'extractor_retries': 3,
            'file_access_retries': 3,
            'merge_output_format': 'mp4',
            'noprogress': True,
            'quiet': True,
            'no_warnings': True,
        }
        return apply_runtime_options(ydl_opts, enable_remote_components=True)

    def _download_url(self, url, ydl_opts):
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def _retry_with_browser_cookies(self, url, base_opts):
        """Retry a blocked YouTube URL using browser cookies if available."""
        last_error = None

        for browser in ("edge", "chrome", "brave"):
            if self.cancel_event.is_set():
                raise Exception("USER_CANCELLED")

            self.after(0, lambda b=browser: self.log(f"INFO: Retrying YouTube with {b} browser cookies..."))
            cookie_opts = dict(base_opts)
            cookie_opts['cookiesfrombrowser'] = (browser, None, None, None)

            try:
                self._download_url(url, cookie_opts)
                self.after(0, lambda b=browser: self.log(f"INFO: Browser cookie fallback worked with {b}."))
                return
            except Exception as exc:
                last_error = str(exc)

        raise Exception(last_error or "Browser cookie fallback failed")

    def _explain_download_error(self, url, error_text):
        """Log a clearer explanation for common site-specific failures."""
        if is_youtube_url(url) and "HTTP Error 403" in error_text:
            self.after(
                0,
                lambda: self.log(
                    "WARNING: YouTube blocked the media request. If Chrome/Edge is open, close it and retry so browser-cookie fallback can work."
                )
            )
        elif "Could not copy Chrome cookie database" in error_text or "Failed to decrypt with DPAPI" in error_text:
            self.after(
                0,
                lambda: self.log(
                    "WARNING: Browser cookies could not be read. Close Chrome/Edge/Brave completely and retry."
                )
            )
        elif is_tiktok_url(url) and "Unable to extract webpage video data" in error_text:
            self.after(
                0,
                lambda: self.log(
                    "WARNING: TikTok changed the page response for this video. This is currently an upstream yt-dlp extraction issue."
                )
            )

    def _start_download(self):
        """Start downloading selected URLs."""
        selected_urls = [link['url'] for link in self.filtered_links if link['var'].get()]
        
        if not selected_urls:
            self.log("⚠️ No URLs selected")
            return
        
        # Apply limit
        try:
            limit = int(self.limit_var.get())
            if limit > 0:
                selected_urls = selected_urls[:limit]
        except:
            pass
        
        self.is_downloading = True
        self.cancel_event.clear()
        self.completed_count = 0
        self.failed_count = 0
        self.total_to_download = len(selected_urls)
        self.counter_label.configure(text="Downloaded: 0")
        
        # Update UI
        self.download_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.log(f"🚀 Starting download of {len(selected_urls)} URLs...")
        
        # Start download thread
        thread = threading.Thread(
            target=self._download_worker,
            args=(selected_urls,),
            daemon=True
        )
        thread.start()
    
    def _download_worker(self, urls):
        """Background download worker."""
        os.makedirs(self.download_dir, exist_ok=True)
        
        partial_count = self._count_partial_files()
        if partial_count:
            self.after(
                0,
                lambda count=partial_count: self.log(
                    f"INFO: Found {count} partial file(s). Link Grabber will start fresh instead of resuming to avoid 403 errors."
                )
            )

        ydl_opts = self._build_ydl_opts()
        
        for i, url in enumerate(urls):
            if self.cancel_event.is_set():
                self.after(0, lambda: self.log("🛑 Download cancelled"))
                break
            
            self.after(0, lambda idx=i+1, total=len(urls): 
                       self.log(f"📥 Downloading {idx}/{total}: {urls[idx-1][:60]}..."))
            
            try:
                self._download_url(url, ydl_opts)
            except Exception as e:
                if "USER_CANCELLED" not in str(e):
                    error_text = str(e)
                    if is_youtube_url(url) and "HTTP Error 403" in error_text:
                        try:
                            self._retry_with_browser_cookies(url, ydl_opts)
                            continue
                        except Exception as fallback_error:
                            error_text = str(fallback_error)

                    self.failed_count += 1
                    self._explain_download_error(url, error_text)
                    self.after(0, lambda err=error_text: self.log(f"❌ Error: {err[:100]}"))
        
        # Complete
        self.after(0, self._on_download_complete)
    
    def _on_download_complete(self):
        """Called when download is complete."""
        self.is_downloading = False
        self.download_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        if not self.cancel_event.is_set():
            if self.failed_count and not self.completed_count:
                self.log(f"⚠️ Download finished with errors. 0 succeeded, {self.failed_count} failed.")
                self.progress_label.configure(text=f"Failed: {self.failed_count}")
            elif self.failed_count:
                self.log(f"⚠️ Download complete with partial failures. {self.completed_count} succeeded, {self.failed_count} failed.")
                self.progress_label.configure(text=f"Done: {self.completed_count}, Failed: {self.failed_count}")
            else:
                self.log(f"✅ Download complete! {self.completed_count} files downloaded.")
                self.progress_label.configure(text="✅ Complete")
        else:
            self.progress_label.configure(text="Stopped")
    
    def _stop_download(self):
        """Stop the current download."""
        self.cancel_event.set()
        self.log("⏹️ Stopping download...")
        self.progress_label.configure(text="Stopping...")
