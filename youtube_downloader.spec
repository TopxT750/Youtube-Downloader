# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

block_cipher = None

project_root = Path(os.getcwd())
src_dir = project_root / "src"
bin_dir = src_dir / "bin"

bin_exes = []
if bin_dir.exists():
    for p in bin_dir.glob("*.exe"):
        # (source, dest folder inside app)
        bin_exes.append((str(p), "bin"))


a = Analysis(
    [str(src_dir / "main.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=bin_exes,
    hiddenimports=[
        # Ensure Qt plugins discovered
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        # yt-dlp dynamic modules
        "yt_dlp",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

icon_file = str(Path('app.ico')) if Path('app.ico').exists() else None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YT-DLP Studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=icon_file,
)


