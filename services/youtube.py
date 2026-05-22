import threading
import os
from yt_dlp import YoutubeDL


class DownloaderService:
    """Simple YouTube downloader service without authentication."""
    
    def __init__(self, callbacks):
        self.callbacks = callbacks
        self.cancel_event = threading.Event()
        self.category_url = {}
    
    def start_download(self, url, options):
        self.cancel_event.clear()
        thread = threading.Thread(target=self._download_worker, args=(url, options), daemon=True)
        thread.start()

    def start_count_check(self, url, options):
        self.cancel_event.clear()
        thread = threading.Thread(target=self._check_count, args=(url, options), daemon=True)
        thread.start()

    def cancel_download(self):
        self.cancel_event.set()
        self.callbacks['log']("🛑 Cancel requested...")

    def _quality_to_format(self, quality):
        """Convert quality setting to yt-dlp format string."""
        if quality == "worst": 
            return "worstvideo*+worstaudio/worst"
        if quality == "best": 
            return "bv*+ba/b"
        # For specific resolutions
        height = quality[:-1]  # Remove 'p' from '720p'
        return f"bv*[height<={height}]+ba/b[height<={height}]/bv*+ba/b"

    def _progress_hook(self, d):
        if self.cancel_event.is_set():
            raise Exception("USER_CANCELLED")
        if d['status'] == 'finished':
            fn = os.path.basename(d.get('filename', ''))
            self.callbacks['log'](f"✓ Downloaded: {fn}")
            if 'update_counter' in self.callbacks:
                self.callbacks['update_counter']()

    def _download_worker(self, url, options):
        """Simple download without authentication."""
        download_dir = options.get('download_dir', './downloads')
        os.makedirs(download_dir, exist_ok=True)
        
        # Modify URL based on selected type
        dl_type = options['type']
        base_url = url.rstrip('/')
        
        # Remove any existing tab path
        for suffix in ['/videos', '/shorts', '/streams', '/featured']:
            if base_url.endswith(suffix):
                base_url = base_url[:-len(suffix)]
        
        # Add the correct tab based on type
        if dl_type == "Long videos":
            url = base_url + '/videos'
            self.callbacks['log']("📹 Downloading LONG VIDEOS only...")
        elif dl_type == "Short videos":
            url = base_url + '/shorts'
            self.callbacks['log']("📱 Downloading SHORTS only...")
        elif dl_type == "Streams":
            url = base_url + '/streams'
            self.callbacks['log']("🔴 Downloading STREAMS only...")
        else:
            self.callbacks['log']("📺 Downloading ALL videos...")
        
        downloaded_count = [0]
        
        def progress_hook(d):
            if self.cancel_event.is_set():
                raise Exception("USER_CANCELLED")
            if d['status'] == 'finished':
                fn = os.path.basename(d.get('filename', ''))
                self.callbacks['log'](f"✓ Downloaded: {fn}")
                downloaded_count[0] += 1
                if 'update_counter' in self.callbacks:
                    self.callbacks['update_counter']()
        
        ydl_opts = {
            'format': self._quality_to_format(options['quality']),
            'outtmpl': os.path.join(download_dir, '%(uploader)s - %(title)s.%(ext)s').replace('\\', '/'),
            'ignoreerrors': True,
            'continuedl': True,
            'nooverwrites': True,
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
        }
        
        if options.get('limit'):
            ydl_opts['playlistend'] = options['limit']
        
        try:
            self.callbacks['log'](f"🎬 Starting download from: {url[:60]}...")
            
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if not self.cancel_event.is_set():
                if downloaded_count[0] > 0:
                    self.callbacks['log'](f"✅ Success! Downloaded {downloaded_count[0]} video(s)")
                else:
                    self.callbacks['log']("⚠️ No videos downloaded - some may require sign-in")
        
        except Exception as e:
            if "USER_CANCELLED" in str(e):
                self.callbacks['log']("🛑 Download cancelled.")
            else:
                self.callbacks['log'](f"❌ Error: {str(e)[:100]}")
        finally:
            if 'on_complete' in self.callbacks:
                self.callbacks['on_complete']()

    def _check_count(self, url, options):
        """Count videos in a channel/playlist."""
        try:
            self.callbacks['log']("🔎 Checking video counts...")
            
            # Store URLs for different categories
            self.category_url = {
                "Long videos": url.rstrip('/') + '/videos',
                "Shorts": url.rstrip('/') + '/shorts',
                "Streams": url.rstrip('/') + '/streams',
            }
            
            counts = {'long': 0, 'shorts': 0, 'streams': 0}
            
            ydl_opts = {
                'extract_flat': 'in_playlist',
                'quiet': True,
                'ignoreerrors': True,
            }
            
            # Count each category
            for category, cat_url in [
                ('long', self.category_url["Long videos"]),
                ('shorts', self.category_url["Shorts"]),
                ('streams', self.category_url["Streams"])
            ]:
                try:
                    with YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(cat_url, download=False)
                        if info and 'entries' in info:
                            counts[category] = len(list(info['entries']))
                except:
                    counts[category] = 0
            
            total = counts['long'] + counts['shorts'] + counts['streams']
            
            self.callbacks['log'](f"✅ Found {total} videos.")
            self.callbacks['log'](f"   • Long: {counts['long']}")
            self.callbacks['log'](f"   • Shorts: {counts['shorts']}")
            self.callbacks['log'](f"   • Streams: {counts['streams']}")
            
            if 'update_total' in self.callbacks:
                self.callbacks['update_total'](total)
        
        except Exception as e:
            self.callbacks['log'](f"❌ Error counting: {str(e)[:80]}")
        finally:
            if 'on_complete' in self.callbacks:
                self.callbacks['on_complete']()