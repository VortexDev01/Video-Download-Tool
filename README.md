# VortexDev Tool

`VortexDev Tool` is a desktop video-downloader utility built with `Python`, `customtkinter`, and `yt-dlp`.

The app provides a dark-themed GUI with three main tools:

- `YouTube` downloader for channels, playlists, and video links
- `TikTok` downloader for account/video URLs
- `Link Grabber` for parsing many URLs at once, filtering them, and downloading selected links

The project is primarily designed for Windows desktop use and includes PyInstaller build files for packaging the app as an `.exe`.

## Features

### 1. YouTube Tab

- Paste a YouTube channel, playlist, or video URL
- Choose download quality: `best`, `1080p`, `720p`, `480p`, `360p`, or `worst`
- Limit how many videos to download
- Select content type:
  - `All videos`
  - `Streams`
  - `Long videos`
  - `Short videos`
- Check total video count before downloading
- Choose or open the download folder
- View activity logs and a simple download counter

### 2. TikTok Tab

- Paste a TikTok account or video URL
- Choose quality and download limit
- Download multiple videos in the background
- Keep a simple `download_history.json` file to avoid re-downloading already processed videos
- Choose or open the download folder
- View logs and download status in the UI

### 3. Link Grabber Tab

- Paste multiple URLs, one per line
- Parse links automatically with regular expressions
- Filter the parsed list by:
  - duplicate URLs
  - blocked domains
  - same-origin domains
  - search text
  - grouped-by-domain view
- Select all, deselect all, or copy selected URLs
- Download only the selected links with `yt-dlp`
- Monitor progress and activity logs while downloading

## Tech Stack

- `Python`
- `customtkinter` for the desktop UI
- `yt-dlp` for media extraction and downloading
- `threading` and `concurrent.futures` for background work
- `PyInstaller` for Windows executable packaging

## Project Structure

```text
app/
|-- app.py
|-- utils.py
|-- requirements.txt
|-- build.bat
|-- pages/
|   |-- youtubepage.py
|   |-- tiktokpage.py
|   `-- linkgrabberpage.py
|-- services/
|   |-- youtube.py
|   |-- tiktok.py
|   `-- downloader.py
|-- components/
|   |-- action_buttons_frame.py
|   |-- options_frame.py
|   |-- status_frame.py
|   |-- url_input_frame.py
|   `-- tiktokgui/
|       |-- button_frame.py
|       |-- optionmenu.py
|       |-- tiktokstatus.py
|       `-- url_input.py
|-- downloads/
|-- dist/
`-- build/
```

## How It Works

### Main Application

`app.py` is the application entry point. It creates the main `customtkinter` window, builds the header and tab navigation, and loads three pages:

- `YouTubePage`
- `TikTokPage`
- `LinkGrabberPage`

Each page manages its own UI and delegates download logic to a service class in the `services/` folder.

### Service Layer

- `services/youtube.py`
  - Handles YouTube downloads and video counting
  - Converts UI quality settings into `yt-dlp` format strings
  - Supports category-based channel downloads such as `/videos`, `/shorts`, and `/streams`

- `services/tiktok.py`
  - Handles TikTok downloads
  - Tracks active downloads and supports cancellation
  - Saves downloaded video IDs into `download_history.json`
  - Uses concurrent workers to improve download throughput

- `pages/linkgrabberpage.py`
  - Contains its own bulk-download flow using `yt-dlp`
  - Parses, filters, selects, and downloads arbitrary URLs from a pasted list

## Installation

### Requirements

- Python `3.x`
- `pip`

### Install Dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` currently includes:

- `yt-dlp`
- `customtkinter`

If you want to build the Windows executable, also install:

```bash
pip install pyinstaller
```

## Run the App

From the project root:

```bash
python app.py
```

By default, downloaded files are saved into the local `downloads/` folder unless a different folder is selected in the UI.

## Build Executable

This project includes a Windows build script:

```bat
build.bat
```

It will:

- activate the local virtual environment if available
- install dependencies
- install `pyinstaller`
- package the application into a Windows executable

The generated file is expected in:

```text
dist/YouTubeDownloader.exe
```

There are also PyInstaller spec files in the root directory:

- `VortexDevTool_v1.spec`
- `YouTubeDownloader.spec`

## Notes and Current Limitations

- The application is desktop-first and appears to be mainly targeted at Windows.
- Some platform download behavior depends on `yt-dlp`, so certain URLs may fail if the source platform changes its restrictions.
- The project contains generated folders such as `build/`, `dist/`, `venv/`, and `__pycache__/`, which are not part of the core source code.
- Some UI text/icons in the source files show encoding issues, but the overall application structure is clear.

## Suggested Cleanup

If you continue developing this project, these improvements would help:

- add a `.gitignore` for `venv/`, `dist/`, `build/`, `downloads/`, and `__pycache__/`
- add proper error handling and user feedback for unsupported/private links
- separate Link Grabber download logic into its own service file
- add tests for URL parsing, option validation, and format selection
- document supported URL types with example inputs

## Summary

This project is a multi-tool desktop downloader application with a custom GUI. It combines YouTube downloading, TikTok downloading, and bulk URL parsing/downloading in a single interface, using `yt-dlp` as the core media download engine.
