import threading
import os
import json
from yt_dlp import YoutubeDL
import time
import re
import concurrent.futures
from utils import resource_path

class DownloadService:
    def __init__(self, callback):
        self.callback = callback
        self.cancel_event = threading.Event()
        self.active_downloads = {}
        self.lock = threading.Lock()
        self.download_history = set()
        self.history_file = "download_history.json"
        self._load_history()

    def _load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.download_history = set(json.load(f))
        except:
            self.download_history = set()

    def _save_history(self):
        try:
            with open(self.history_file, 'w') as f:
                json.dump(list(self.download_history), f)
        except:
            pass

    def tiktok_start_download(self, url, option):
        with self.lock:
            # Clean up any cancelled downloads first
            cancelled_urls = [url for url, info in self.active_downloads.items() if info.get('cancelled')]
            for cancelled_url in cancelled_urls:
                del self.active_downloads[cancelled_url]
            
            if url in self.active_downloads:
                self.callback['log']("ℹ️ Download already in progress for this URL")
                return False
            
            self.active_downloads[url] = {
                'thread': None,
                'cancelled': False,
                'completed': False,
                'downloaded_count': 0
            }
        
        self.cancel_event.clear()
        thread = threading.Thread(target=self._download_worker, args=(url, option), daemon=True)
        
        with self.lock:
            self.active_downloads[url]['thread'] = thread
        
        thread.start()
        return True

    def tiktok_cancel_download(self, url=None):
        cancelled_urls = []
        
        with self.lock:
            if url:
                if url in self.active_downloads and not self.active_downloads[url]['cancelled']:
                    self.active_downloads[url]['cancelled'] = True
                    cancelled_urls.append(url)
                    self.callback['log'](f"🛑 Cancel requested for {url}")
            else:
                self.cancel_event.set()
                for current_url, download_info in self.active_downloads.items():
                    if not download_info['cancelled']:
                        download_info['cancelled'] = True
                        cancelled_urls.append(current_url)
                if cancelled_urls:
                    self.callback['log']("🛑 Cancel all requested...")
        
        return len(cancelled_urls) > 0

    def clear_download_history(self):
        with self.lock:
            self.download_history.clear()
            self._save_history()
        self.callback['log']("📋 Download history cleared")

    def _quality_to_format(self, quality):
        quality_map = {
            "1080p": "best[height<=1080]",
            "720p": "best[height<=720]",
            "480p": "best[height<=480]",
            "360p": "best[height<=360]"
        }
        return quality_map.get(quality, "best")

    def _progress_hook(self, d, url, video_title=""):
        with self.lock:
            if url in self.active_downloads and self.active_downloads[url]['cancelled']:
                raise Exception("USER_CANCELLED")
                
        if d['status'] == 'downloading':
            # Show download progress
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            if video_title:
                self.callback['log'](f"📥 Downloading {video_title}: {percent} at {speed}, ETA: {eta}")
                
        elif d['status'] == 'finished':
            fn = os.path.basename(d.get('filename', ''))
            video_id = self._extract_video_id(d)
            
            if video_id:
                with self.lock:
                    if video_id not in self.download_history:
                        self.download_history.add(video_id)
                        self._save_history()
                        if url in self.active_downloads:
                            self.active_downloads[url]['downloaded_count'] += 1
                        self.callback['log'](f"✅ Downloaded: {fn}")
                        if 'update_counter' in self.callback:
                            self.callback['update_counter']()
                    else:
                        self.callback['log'](f"ℹ️ Already downloaded: {fn}")

    def _extract_video_id(self, d):
        try:
            if hasattr(d, 'get') and d.get('info_dict'):
                info_dict = d['info_dict']
                video_id = info_dict.get('id') or info_dict.get('display_id')
                if video_id:
                    return video_id
            
            filename = d.get('filename', '')
            id_pattern = r'\[(\d{18,21})\]'
            match = re.search(id_pattern, filename)
            if match:
                return match.group(1)
            
            return None
        except:
            return None

    def _clean_filename(self, title):
        """Clean the title to make it safe for filenames"""
        if not title:
            return "tiktok_video"
        
        # Remove invalid characters for filenames
        title = re.sub(r'[<>:"/\\|?*]', '', title)
        
        # Limit length to avoid issues with long filenames
        if len(title) > 100:
            title = title[:100] + "..."
        
        return title

    def _extract_hashtags(self, description):
        """Extract hashtags from video description"""
        if not description:
            return ""
        
        hashtags = re.findall(r'#\w+', description)
        if hashtags:
            # Limit to 3 hashtags to avoid long filenames
            return " " + " ".join(hashtags[:3])
        return ""

    def _download_single_video(self, video_url, download_dir, quality, url, video_title, video_id):
        """Download a single video with optimized settings"""
        def progress_hook(d):
            return self._progress_hook(d, url, video_title)
        
        # Clean title and extract hashtags
        clean_title = self._clean_filename(video_title)
        hashtags = self._extract_hashtags(video_title)  # Using title as description
        
        # Create custom filename template with title and hashtags
        filename_template = f"{clean_title}{hashtags}.%(ext)s"
        ffmpeg_path = resource_path(".")
        
        # Optimized download options for speed
        ydl_opts = {
            'format': self._quality_to_format(quality),
            'outtmpl': os.path.join(download_dir, filename_template),
            'progress_hooks': [progress_hook],
            'ignoreerrors': True,
            'noprogress': True,
            'quiet': True,
            'socket_timeout': 15,  # Reduced timeout
            'retries': 2,  # Reduced retries
            'nooverwrites': True,
            'http_chunk_size': 10485760,  # 10MB chunks for faster downloading
            'continuedl': True,
            'nopart': False,  # Enable partial downloads
            'buffersize': 65536,  # Larger buffer size
            'extract_flat': False,
            'concurrent_fragment_downloads': 4,  # Parallel fragment downloads
            'ffmpeg_location': ffmpeg_path,
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            return True
        except Exception as e:
            if "USER_CANCELLED" in str(e):
                raise
            self.callback['log'](f"⚠️ Error downloading {clean_title}: {str(e)}")
            return False

    def _validate_options(self, options):
        """Validate and sanitize download options"""
        validated = options.copy()
        
        # Ensure limit is a positive integer or 0 (0 means download all)
        limit = validated.get('limit', 0)
        if limit is None or not isinstance(limit, int) or limit < 0:
            validated['limit'] = 0
        
        # Ensure quality is a valid string
        quality = validated.get('quality', 'best')
        if not quality or not isinstance(quality, str):
            validated['quality'] = 'best'
        
        # Ensure download_dir exists
        download_dir = validated.get('download_dir', './downloads')
        if not download_dir or not isinstance(download_dir, str):
            validated['download_dir'] = './downloads'
        
        return validated

    def _download_worker(self, url, options):
        try:
            # Validate options first
            options = self._validate_options(options)
            download_dir = options.get('download_dir', './downloads')
            os.makedirs(download_dir, exist_ok=True)
            quality = options.get('quality', 'best')
            download_limit = options.get('limit', 0)
            
            # Set up periodic cancellation check
            def should_cancel():
                with self.lock:
                    return url in self.active_downloads and self.active_downloads[url]['cancelled']

            if should_cancel():
                raise Exception("USER_CANCELLED")

            # First, extract all video information
            self.callback['log']("🔍 Extracting video information...")
            
            # Use a simple YDL instance just for info extraction
            info_ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'extract_flat': False,
            }
            
            with YoutubeDL(info_ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            if not info or 'entries' not in info:
                self.callback['log']("❌ No videos found or invalid URL")
                return
            
            entries = list(info['entries'])
            total_videos = len(entries)
            
            # Filter out already downloaded videos
            new_entries = []
            for entry in entries:
                if entry:
                    video_id = entry.get('id') or entry.get('display_id')
                    if video_id and video_id not in self.download_history:
                        new_entries.append(entry)
            
            new_videos = len(new_entries)
            self.callback['log'](f"📊 Found {total_videos} videos ({new_videos} new)")
            
            if new_videos == 0:
                self.callback['log']("ℹ️ No new videos to download")
                return
            
            # Apply download limit (0 means download all)
            if download_limit > 0:
                entries_to_download = new_entries[:download_limit]
                self.callback['log'](f"📥 Downloading {len(entries_to_download)} videos (limit: {download_limit})...")
            else:
                entries_to_download = new_entries
                self.callback['log'](f"📥 Downloading all {len(entries_to_download)} new videos...")
            
            if should_cancel():
                raise Exception("USER_CANCELLED")

            # Download videos with limited concurrency for better performance
            max_workers = min(3, len(entries_to_download))  # Limit concurrent downloads
            downloaded_count = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_video = {}
                
                for i, entry in enumerate(entries_to_download):
                    if should_cancel():
                        raise Exception("USER_CANCELLED")
                    
                    video_url = entry.get('webpage_url') or entry.get('url')
                    if not video_url:
                        continue
                    
                    video_id = entry.get('id') or entry.get('display_id')
                    title = entry.get('title', 'tiktok_video')
                    
                    self.callback['log'](f"⬇️ Queueing: {self._clean_filename(title)}")
                    
                    # Submit download task to thread pool
                    future = executor.submit(
                        self._download_single_video,
                        video_url, download_dir, quality, url, title, video_id
                    )
                    future_to_video[future] = (i, title)
                
                # Process completed downloads
                for future in concurrent.futures.as_completed(future_to_video):
                    if should_cancel():
                        raise Exception("USER_CANCELLED")
                    
                    i, title = future_to_video[future]
                    try:
                        success = future.result()
                        if success:
                            downloaded_count += 1
                            self.callback['log'](f"✅ Finished: {self._clean_filename(title)}")
                    except Exception as e:
                        self.callback['log'](f"⚠️ Failed: {self._clean_filename(title)} - {str(e)}")
            
            with self.lock:
                if url in self.active_downloads and not self.active_downloads[url]['cancelled']:
                    self.active_downloads[url]['completed'] = True
                    self.callback['log'](f"🎉 Successfully downloaded {downloaded_count} videos!")

        except Exception as e:
            with self.lock:
                cancelled = url in self.active_downloads and self.active_downloads[url]['cancelled']
            
            if "USER_CANCELLED" in str(e) or cancelled:
                self.callback['log']("🛑 Download cancelled.")
            else:
                self.callback['log'](f"❌ Error: {str(e)}")
        finally:
            with self.lock:
                if url in self.active_downloads:
                    if not self.active_downloads[url].get('completed', False):
                        del self.active_downloads[url]
            
            if 'on_complete' in self.callback:
                self.callback['on_complete']()

    def is_downloading(self, url=None):
        with self.lock:
            if url:
                return url in self.active_downloads and not self.active_downloads[url].get('cancelled', False)
            return any(not info.get('cancelled', False) for info in self.active_downloads.values())

    def cleanup_cancelled(self):
        with self.lock:
            cancelled_urls = [url for url, info in self.active_downloads.items() if info.get('cancelled')]
            for url in cancelled_urls:
                del self.active_downloads[url]
            if cancelled_urls:
                self.callback['log'](f"🧹 Cleaned up {len(cancelled_urls)} cancelled downloads")