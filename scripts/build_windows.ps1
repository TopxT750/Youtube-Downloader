param(
    [switch]$FetchTools
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Push-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
Push-Location ..

if (-not (Test-Path .venv)) {
  py -3 -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install pyinstaller

if ($FetchTools) {
  # Pre-fetch ffmpeg & aria2c into src/bin for bundling
  $pythonCode = @'
from utils.ffmpeg import ensure_ffmpeg
from utils.aria2 import ensure_aria2c
ensure_ffmpeg()
ensure_aria2c()
print("Fetched ffmpeg/aria2c")
'@
  $env:PYTHONPATH = "$(Get-Location)\src"
  $pythonCode | .\.venv\Scripts\python.exe -
}

# Convert PNG icon to ICO for PyInstaller
$iconPng = Join-Path (Get-Location) 'icon_transparent.png'
$iconIco = Join-Path (Get-Location) 'app.ico'
if (Test-Path $iconPng) {
  $py = @'
from PIL import Image
import sys
png, ico = sys.argv[1], sys.argv[2]
img = Image.open(png).convert("RGBA")
img.save(ico, sizes=[(256,256),(128,128),(64,64),(32,32),(16,16)])
'@
  $py | .\.venv\Scripts\python.exe - $iconPng $iconIco
}

.\.venv\Scripts\pyinstaller.exe --noconfirm youtube_downloader.spec

Pop-Location
Pop-Location

Write-Host "Build complete. Output in 'dist/YoutubeDownloader'"


