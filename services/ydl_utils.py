import shutil
from urllib.parse import urlparse


class QuietYDLLogger:
    """Suppress yt-dlp console noise; the app handles user-facing logging itself."""

    def debug(self, msg):
        return None

    def warning(self, msg):
        return None

    def error(self, msg):
        return None


def detect_js_runtimes():
    """Enable optional JS runtimes only when they exist on this machine."""
    runtimes = {}
    for runtime in ("deno", "node"):
        if shutil.which(runtime):
            runtimes[runtime] = {}
    return runtimes


def apply_runtime_options(ydl_opts, *, enable_remote_components=False):
    """Add shared yt-dlp runtime options used by the desktop app."""
    opts = dict(ydl_opts)
    opts.setdefault("logger", QuietYDLLogger())

    js_runtimes = detect_js_runtimes()
    if js_runtimes:
        opts["js_runtimes"] = js_runtimes
        if enable_remote_components:
            opts["remote_components"] = {"ejs:github"}

    return opts


def is_youtube_url(url):
    host = urlparse(url).netloc.lower()
    return "youtube.com" in host or "youtu.be" in host


def is_tiktok_url(url):
    return "tiktok.com" in urlparse(url).netloc.lower()

