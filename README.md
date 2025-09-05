## Youtube Downloader GUI (yt-dlp)

Windows-friendly GUI for `yt-dlp`, inspired by `ytdlp-gui` layout.

- Queue multiple URLs
- Choose format and output folder
- Per-item progress, speed, ETA, and logs
- Light/Dark theme toggle

Reference: [`2025.8.20` release](https://github.com/aliencaocao/ytdlp-gui/releases/tag/2025.8.20)

### Setup

```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

### Run

```bash
python src/main.py
```

FFmpeg and aria2c are auto-downloaded on demand into `src/bin/` and used automatically (FFmpeg always, aria2c when enabled in Settings). No system install required.

### Settings

- Settings -> Download Settings: toggle bundled aria2c, set concurrent fragments, and choose a default downloads folder.

### Build Windows EXE

```powershell
# From project root
scripts\build_windows.ps1 -FetchTools

# Result:
# dist\YoutubeDownloader\YoutubeDownloader.exe (portable folder)
```

Notes:
- The build script fetches FFmpeg and aria2c first so they are bundled under `bin/`.
- The `.spec` file includes `src/bin/*.exe` into the app automatically.

