# YouTube Downloader GUI (yt-dlp)

A Windows-friendly GUI for yt-dlp, inspired by the ytdlp-gui layout.

- Queue multiple URLs
- Choose format/quality (including 4K where available) and output folder
- Per-item progress, speed, ETA, and logs
- Light/Dark theme toggle
- Zero system installs: FFmpeg and aria2c are auto-fetched and used automatically

Reference build: 2025.8.20 release

## Requirements

- Windows 10/11 (64-bit)
- Python 3.9+ (recommended 3.10+)
- Internet access on first run (to fetch FFmpeg and aria2c if enabled)


## Quick Start

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Alternative (CMD):

```cmd
.venv\Scripts\activate.bat
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python src/main.py
```


On first launch, FFmpeg (always) and aria2c (when enabled in Settings) are auto-downloaded into `src/bin/` and used automatically. No system-wide installs required.

## How to Use

- Add URLs:
    - Paste one or more video/playlist URLs into the queue.
- Choose output:
    - Set the output folder (per item or as a default).
- Pick format/quality:
    - Select `bestvideo+bestaudio` for highest quality; 2160p (4K) when available.
    - Note: 4K availability depends on the source; merging uses FFmpeg.
- Start downloads:
    - Monitor per-item progress, speed, ETA, and log output.
- Theme:
    - Toggle Light/Dark theme in the UI.


## Settings

Settings → Download Settings:

- Use bundled aria2c:
    - Enables aria2c for fragmented streams; may improve speed on some connections.
- Concurrent fragments:
    - Controls parallel segment fetching. Higher values can speed up downloads but may stress networks.
- Default downloads folder:
    - Sets a global default for new items.

Notes:

- FFmpeg is always used for muxing/merging when required by the selected format.
- aria2c is only used when enabled here.


## Tips for 4K Downloads

- Choose `bestvideo+bestaudio` (or highest available) to get 2160p when the source provides it.
- Ensure sufficient disk space; high-bitrate 4K files can be large.
- Merging large files uses FFmpeg; slower disks can increase total processing time.


## Updating

- Update dependencies (including yt-dlp) to the versions pinned in `requirements.txt`:

```bash
pip install -U -r requirements.txt
```

- If you change versions manually, re-test downloads and merging for compatibility.


## Troubleshooting

- Slow downloads:
    - Enable aria2c and increase concurrent fragments moderately.
    - Try a different network or pause other heavy traffic.
- 4K not appearing:
    - Not all videos provide 4K; try `bestvideo+bestaudio`.
    - Some 4K formats are video-only; FFmpeg will merge with audio automatically.
- Permission or SSL errors:
    - Run PowerShell without restrictive execution policies and ensure firewalls/proxies allow traffic.
- FFmpeg/aria2c not found:
    - They are auto-downloaded into `src/bin/` on first use; ensure the app can write to that folder.


## Privacy and Legal

- Download only content you own or have permission to download.
- Respect YouTube’s Terms of Service and local laws.
- No telemetry is sent by this app; network requests are made by yt-dlp/FFmpeg/aria2c to fetch media.


## Acknowledgements

- yt-dlp for core downloading
- FFmpeg for media processing
- aria2c for segmented downloads
- ytdlp-gui for layout inspiration


## License

See `LICENSE` in this repository.

