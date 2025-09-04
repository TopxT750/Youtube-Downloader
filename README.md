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

FFmpeg should be on PATH for merging.

