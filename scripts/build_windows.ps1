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

.\.venv\Scripts\pyinstaller.exe --noconfirm youtube_downloader.spec

Pop-Location
Pop-Location

Write-Host "Build complete. Output in 'dist/YoutubeDownloader'"


