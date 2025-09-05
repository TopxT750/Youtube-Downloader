## YT-DLP Studio

A fast, simple, and powerful Windows GUI for `yt-dlp` with everything bundled. No setup headaches: the app can download high‑quality videos and audio from popular sites with a clean UI, progress bars, and smart speed options.

Inspired by the look and ergonomics of community GUIs such as the `ytdlp-gui` project (see their 2025.8.20 release notes for reference) [`link`](https://github.com/aliencaocao/ytdlp-gui/releases/tag/2025.8.20).

### Highlights (Layman’s terms)

- One app, no extra installs: FFmpeg included; optional faster engine (aria2c) is one click away.
- Paste links, click Start, watch the progress bar fill up.
- Download just audio (MP3/M4A) or full video. Choose where files are saved.
- See download speed and time remaining. Dark mode supported.
- “Power Download…” for experts: pick file type (MP4/MKV/WEBM) and quality.
- Build a single EXE you can carry on a USB stick.

### Feature Overview (Technical)

- GUI: PySide6 (Qt 6) desktop app.
- Downloader: `yt-dlp` (2025.8.20), with progress hooks → per‑item and overall progress.
- Media tools: FFmpeg auto-fetched and invoked via `ffmpeg_location`.
- Optional external downloader: aria2c auto-fetched; toggle in Settings. Configurable concurrent fragment count.
- Queue: multi-URL queue, auto-continue, status per row.
- Advanced options: container (merge_output_format), video height constraints, audio extraction bitrate.
- ANSI‑free progress strings; progress bar with centered percentage.
- Single‑file packaging via PyInstaller (Windows x64). Icon and app name embedded.

### Quick Start

```powershell
# 1) Create a venv and install deps (Windows PowerShell)
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2) Run the app
python src\main.py
```

Notes
- On first run the app downloads FFmpeg into `src/bin/`. If you enable the Faster Engine in Settings, aria2c will also be fetched.

### Using the App

1) Paste one or more links in the URL box and click “Add to Queue”.
2) Select output quality (e.g., Best video+audio, Audio only) and choose an output folder.
3) Click Start. Each row shows: Title, Progress bar with percent, Speed, ETA, and Status.
4) The Overall bar shows the average progress across items.
5) Use View → Toggle Theme to switch light/dark.

Power Download (for advanced users)
- Container: choose MP4/MKV/WEBM.
- Video quality: Best, or constrain by height (1080p/720p/480p).
- Audio quality: Best, or pick a target bitrate (160k/128k). Audio extraction uses FFmpeg.

Download Settings (friendly labels)
- Use Faster Engine (recommended): turn on aria2c for faster HTTP downloads.
- Speed mode: Normal / Faster / Fastest (maps to safe fragment concurrency levels behind the scenes).
- Default downloads folder: set where files go by default; also available on the main screen.

### Building a Single EXE (standalone)

This produces a single executable (no sidecar files).

```powershell
# From project root
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_windows.ps1 -FetchTools

# Output
# dist\YT-DLP Studio.exe  (single-file EXE)
```

Tips
- Single‑file EXEs unpack to a temp directory on first launch; that’s normal. If you want the fastest startup, use a folder build instead (we can provide an alternative spec if needed).
- If Defender is suspicious (common for unsigned packed EXEs), consider code signing the output.

### Troubleshooting

- No Python? Install Python 3.11+ for Windows and ensure the `py` launcher is enabled, or use `python` on PATH.
- Slow speeds? Enable “Use Faster Engine” in Settings and set Speed mode to Fastest.
- Merge failures? Ensure FFmpeg was fetched (first run) or re‑run with the `-FetchTools` build step.
- Site error on a specific link? Update `yt-dlp` to the referenced version or newer.

### Contributing

We welcome contributions of all kinds (bug reports, feature requests, PRs).

Fork & clone
```bash
# On GitHub: Click Fork on the repository page, then
git clone https://github.com/<your-username>/<your-fork>.git
cd <your-fork>
```

Create a branch
```bash
git checkout -b feat/my-improvement
```

Install and run
```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python src/main.py
```

Make your changes
- Follow the existing code style; prefer explicit, readable names and small functions.
- Test UI flows: adding to queue, starting downloads, toggling theme, Power Download dialog, Settings dialog.

Commit and push
```bash
git add -A
git commit -m "feat: describe your change"
git push origin feat/my-improvement
```

Open a Pull Request
- Describe the change, why it helps, and how to test it.
- Include screenshots/GIFs for UI changes when possible.

### License and Credits

- Built on `yt-dlp`, `FFmpeg`, `aria2c`, and `PySide6`. Huge thanks to their communities.
- UI inspired by community tools like `ytdlp-gui` [`link`](https://github.com/aliencaocao/ytdlp-gui/releases/tag/2025.8.20).
