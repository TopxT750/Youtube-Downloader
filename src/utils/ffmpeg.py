from __future__ import annotations

import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional
import urllib.request


BIN_DIR = Path(__file__).resolve().parent.parent / "bin"
FFMPEG_EXE = BIN_DIR / "ffmpeg.exe"
FFPROBE_EXE = BIN_DIR / "ffprobe.exe"

# Gyan.dev latest release (static build) link pattern; stable URL
FFMPEG_ZIP_URL = (
    "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z"  # 7z preferred, but we use fallback zip
)

# We will use a known zipped mirror when 7z is not available
FFMPEG_ZIP_FALLBACK = (
    "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
)


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def ensure_ffmpeg() -> Optional[str]:
    """Ensure ffmpeg.exe exists in local bin, return its directory for yt-dlp.

    Returns the directory path as string if available, or None on failure.
    """
    # If already present, return folder
    if FFMPEG_EXE.exists() and FFPROBE_EXE.exists():
        return str(BIN_DIR)

    # Try download fallback ZIP (zip is supported by stdlib)
    try:
        with tempfile.TemporaryDirectory() as td:
            tmp_zip = Path(td) / "ffmpeg.zip"
            _download(FFMPEG_ZIP_FALLBACK, tmp_zip)
            with zipfile.ZipFile(tmp_zip, "r") as zf:
                # Find the bin directory inside the extracted folder
                root_dir_name = None
                for name in zf.namelist():
                    if name.endswith("/bin/ffmpeg.exe"):
                        root_dir_name = name.split("/bin/")[0]
                        break
                if root_dir_name is None:
                    # Extract all and search
                    zf.extractall(td)
                    extracted = Path(td)
                    candidates = list(extracted.rglob("ffmpeg.exe"))
                    if not candidates:
                        return None
                    src_ffmpeg = candidates[0]
                    src_ffprobe = src_ffmpeg.parent / "ffprobe.exe"
                else:
                    # Extract only needed files
                    ffmpeg_member = f"{root_dir_name}/bin/ffmpeg.exe"
                    ffprobe_member = f"{root_dir_name}/bin/ffprobe.exe"
                    zf.extract(ffmpeg_member, td)
                    zf.extract(ffprobe_member, td)
                    src_ffmpeg = Path(td) / ffmpeg_member
                    src_ffprobe = Path(td) / ffprobe_member

                BIN_DIR.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_ffmpeg, FFMPEG_EXE)
                if src_ffprobe.exists():
                    shutil.copy2(src_ffprobe, FFPROBE_EXE)
        return str(BIN_DIR)
    except Exception:
        return None


