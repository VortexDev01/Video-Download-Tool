import threading
import os
from yt_dlp import YoutubeDL

class DownloaderService:
    def __init__(self, callbacks):
        self.callbacks = callbacks
        self.cancel_event = threading.Event()
        self.category_url = {}
        self.cookies_file = None  # Path to cookies.txt file for YouTube authentication
        self.browser_cookies = None  # Browser name for cookie extraction
    
    def set_cookies_file(self, path):
        """Set the path to the cookies file for YouTube authentication."""
        self.cookies_file = path if path and os.path.exists(path) else None
        self.browser_cookies = None  # Disable browser cookies when using file
    
    def set_browser_cookies(self, browser_name):
        """Set the browser to extract cookies from (chrome, edge, firefox, brave, etc.)."""
        self.browser_cookies = browser_name
        if browser_name:
            self.cookies_file = None  # Disable cookies file when using browser
    
    def _get_auth_opts(self):
        """Get authentication options based on current mode."""
        opts = {
            # Reduce concurrent downloads to avoid IP flagging
            'concurrent_fragment_downloads': 1,
            # Add small sleep between downloads
            'sleep_interval': 2,
            'max_sleep_interval': 5,
            # Use 'web' client to align with Desktop Chrome cookies
            # This prevents "Session/Client Mismatch" that causes empty files
            'extractor_args': {'youtube': {'player_client': ['web']}},
            # Force FFmpeg for HLS streams (harder to detect/throttle)
            'hls_prefer_native': False,
            # Socket timeout
            'socket_timeout': 30,
            # Don't abort on unavailable fragments
            'skip_unavailable_fragments': True,
            # Retries for network errors
            'retries': 10,
            'fragment_retries': 10,
            # Don't check certificates
            'nocheckcertificate': True,
        }
        
        if self.browser_cookies:
            # Extract cookies directly from browser (browser must be closed!)
            opts['cookiesfrombrowser'] = (self.browser_cookies,)
        elif self.cookies_file:
            opts['cookiefile'] = self.cookies_file
        
        return opts

    def start_download(self, url, options):
        self.cancel_event.clear()
        thread = threading.Thread(target=self._download_worker, args=(url, options), daemon=True)
        thread.start()

    def start_count_check(self, url, options):
        """Start thread for counting videos"""
        self.cancel_event.clear()
        thread = threading.Thread(target=self._check_count, args=(url, options), daemon=True)
        thread.start()

    def cancel_download(self):
        self.cancel_event.set()
        self.callbacks['log']("🛑 Cancel requested...")

    def _quality_to_format(self, quality):
        if quality == "worst": return "worst"
        if quality == "best": return "best"
        # For specific resolutions, ensure video-only and then merge with best audio
        return f"bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]"


    def _progress_hook(self, d):
        if self.cancel_event.is_set():
            raise Exception("USER_CANCELLED")
        if d['status'] == 'finished':
            fn = os.path.basename(d.get('filename', ''))
            self.callbacks['log'](f"✓ Completed: {fn}")
            if 'update_counter' in self.callbacks:
                self.callbacks['update_counter']()

    def _download_worker(self, url, options):
        try:
            download_dir = options.get('download_dir', './downloads')
            os.makedirs(download_dir, exist_ok=True)
            
            ydl_opts = {
                'format': self._quality_to_format(options['quality']),
                'outtmpl': os.path.join(download_dir, '%(uploader)s - %(title)s.%(ext)s').replace('\\','/'),
                'progress_hooks': [self._progress_hook],
                'ignoreerrors': False,
                'continuedl': True,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }
            
            # Add authentication options (OAuth2 or cookies)
            ydl_opts.update(self._get_auth_opts())

            dl_type = options['type']
            if dl_type != "All videos" and dl_type in self.category_url:
                url = self.category_url[dl_type]

            if options['limit']:
                ydl_opts['playlistend'] = options['limit']

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if not self.cancel_event.is_set():
                self.callbacks['log']("✅ Download process finished!")

        except Exception as e:
            if "USER_CANCELLED" in str(e):
                self.callbacks['log']("🛑 Download cancelled.")
            else:
                self.callbacks['log'](f"❌ Error: {e}")
        finally:
            if 'on_complete' in self.callbacks:
                self.callbacks['on_complete']()

    def _count_videos_fast(self, url: str) -> int:
        """Use yt-dlp library for fast counting, avoiding subprocess."""
        try:
            ydl_opts = {
                'extract_flat': 'in_playlist',
                'quiet': True,
                'ignoreerrors': True,
            }
            
            # Add authentication options (OAuth2 or cookies)
            ydl_opts.update(self._get_auth_opts())
            
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                # For playlists/channels, info_dict will contain 'entries'
                if info_dict and 'entries' in info_dict and info_dict['entries'] is not None:
                    return len(info_dict['entries'])
            return 0 # Return 0 if no entries are found or info_dict is None
        except Exception:
            # In case of any other errors from yt-dlp library
            return 0

    def _check_count(self, url, options):
        """
        Fast counting by type using threads to run checks concurrently.
        - /videos -> long uploads
        - /shorts -> shorts
        - /streams -> livestreams
        """
        try:
            video_type = options.get('type')
            channel = url.rstrip("/")
            if channel.endswith(("/videos", "/shorts", "/streams")):
                channel = channel.rsplit("/", 1)[0]

            urls = {
                "Long videos": f"{channel}/videos",
                "Short videos": f"{channel}/shorts",
                "Streams": f"{channel}/streams",
            }

            self.callbacks['log']("🔎 Checking video counts (this may take a moment)...")
            
            counts = {}
            threads = []

            # Helper function to be run in each thread
            def _fetch_count(category, category_url):
                count = self._count_videos_fast(category_url)
                counts[category] = count
                self.category_url[category] = category_url

            # Create and start a thread for each category
            if video_type in urls:
                # If a specific type is selected, only count that type
                thread = threading.Thread(target=_fetch_count, args=(video_type, urls[video_type]))
                threads.append(thread)
                thread.start()
            else: # 'All videos' or other cases
                for category, category_url in urls.items():
                    thread = threading.Thread(target=_fetch_count, args=(category, category_url))
                    threads.append(thread)
                    thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            total = sum(counts.values())

            if 'update_total' in self.callbacks:
                if video_type == 'All videos':
                    self.callbacks['update_total'](
                        f"Total: {total} (Long: {counts.get('Long videos', 0)}, Shorts: {counts.get('Short videos', 0)}, Streams: {counts.get('Streams', 0)})"
                    )
                elif video_type in counts:
                    self.callbacks['update_total'](
                        f"Total {video_type}: {counts.get(video_type, 0)}"
                    )
                else:
                    self.callbacks['update_total'](
                        f"Total: {total}"
                    )

            self.callbacks['log'](
                f"✅ Found {total} videos.\n" 
                f"   • Long: {counts.get('Long videos', 0)}\n" 
                f"   • Shorts: {counts.get('Short videos', 0)}\n" 
                f"   • Streams: {counts.get('Streams', 0)}"
            )

        except Exception as e:
            if 'update_total' in self.callbacks:
                self.callbacks['update_total']("Total videos: Error")
            self.callbacks['log'](f"❌ Error checking total: {e}")
        finally:
            if "on_count_complete" in self.callbacks:
                self.callbacks['on_complete']()