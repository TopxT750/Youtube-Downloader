from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional
import urllib.request


BIN_DIR = Path(__file__).resolve().parent.parent / "bin"
ARIA2_EXE = BIN_DIR / "aria2c.exe"

# Official GitHub releases URL pattern (portable Windows build packaged as zip)
# Using a stable, recent mirror that provides aria2c.exe inside bin folder
ARIA2_ZIP_URL = (
    "https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip"
)


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def ensure_aria2c() -> Optional[str]:
    """Ensure aria2c.exe exists in local bin, return its path directory."""
    if ARIA2_EXE.exists():
        return str(BIN_DIR)
    try:
        with tempfile.TemporaryDirectory() as td:
            tmp_zip = Path(td) / "aria2.zip"
            _download(ARIA2_ZIP_URL, tmp_zip)
            with zipfile.ZipFile(tmp_zip, "r") as zf:
                zf.extractall(td)
            extracted = Path(td)
            candidate = next(extracted.rglob("aria2c.exe"), None)
            if candidate is None:
                return None
            BIN_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, ARIA2_EXE)
        return str(BIN_DIR)
    except Exception:
        return None


