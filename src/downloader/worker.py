from __future__ import annotations

from typing import Callable, Optional, Any, Dict
from PySide6.QtCore import QObject, Signal, QThread
import yt_dlp as ytdlp
import os
import re
from utils.ffmpeg import ensure_ffmpeg
from utils.settings import AppSettings
from utils.aria2 import ensure_aria2c


class DownloadSignals(QObject):
    progress = Signal(int, str, str, str)  # percent, speed_str, eta_str, status
    title = Signal(str)
    log = Signal(str)
    finished = Signal(bool, str)  # success, filepath


class DownloadWorker(QThread):
    def __init__(
        self,
        url: str,
        output_dir: str,
        format_mode: str,
        advanced_options: dict | None = None,
    ) -> None:
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.format_mode = format_mode
        self.advanced_options = advanced_options or {}
        self.signals = DownloadSignals()

    @staticmethod
    def _strip_ansi(value: str) -> str:
        if not value:
            return value
        ansi_re = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        return ansi_re.sub("", value)

    def _select_format(self) -> str:
        if self.format_mode == "Audio only (m4a)":
            return "bestaudio[ext=m4a]/bestaudio/best"
        if self.format_mode == "Audio only (mp3)":
            return "bestaudio/best"
        if self.format_mode == "Best video only":
            return "bestvideo/best"
        return "bestvideo+bestaudio/best"

    def _progress_hook(self, d: Dict[str, Any]) -> None:
        if d.get("status") == "downloading":
            percent = d.get("_percent_str", "0.0%").strip().replace("%", "")
            try:
                pct = float(percent)
            except Exception:
                pct = 0.0
            speed = self._strip_ansi(d.get("_speed_str") or "")
            eta = self._strip_ansi(d.get("_eta_str") or "")
            self.signals.progress.emit(int(pct), speed, eta, "Downloading")
        elif d.get("status") == "finished":
            self.signals.log.emit("Merging/processing...")

    def run(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        settings = AppSettings.load()
        # Speed tuning options: use concurrent fragment downloads if supported,
        # and aria2c if the user has it installed (yt-dlp auto-detects when "external_downloader": "aria2c")
        ydl_opts: Dict[str, Any] = {
            "progress_hooks": [self._progress_hook],
            "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
            "noprogress": True,
            "ignoreerrors": True,
            "merge_output_format": "mp4",
            "format": self._select_format(),
            "postprocessors": [],
            "no_color": True,
            # Try to accelerate large downloads
            "concurrent_fragment_downloads": max(1, int(settings.concurrent_fragments or 8)),
            "retries": 20,
            "fragment_retries": 20,
            "throttled_rate": 0,
        }
        # Apply advanced options
        container = self.advanced_options.get("container") if isinstance(self.advanced_options, dict) else None
        if container in {"mp4", "mkv", "webm"}:
            ydl_opts["merge_output_format"] = container
        vq = self.advanced_options.get("video_quality") if isinstance(self.advanced_options, dict) else None
        if isinstance(vq, str) and vq.lower() != "best":
            try:
                height = int(vq.replace("p", ""))
                ydl_opts["format"] = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
            except Exception:
                pass
        aq = self.advanced_options.get("audio_quality") if isinstance(self.advanced_options, dict) else None
        if isinstance(aq, str) and aq.lower() != "best":
            ydl_opts["postprocessors"].append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3" if (container or "mp4") == "mp4" else "m4a",
                    "preferredquality": aq.replace("k", ""),
                }
            )
        ffdir = ensure_ffmpeg()
        if ffdir:
            ydl_opts["ffmpeg_location"] = ffdir
        if settings.use_aria2c:
            ardir = ensure_aria2c()
            if ardir:
                ydl_opts["external_downloader"] = "aria2c"
                ydl_opts["external_downloader_args"] = {
                    "aria2c": [
                        "-x16",
                        "-s16",
                        "-j16",
                        "--min-split-size=1M",
                        "--max-connection-per-server=16",
                    ]
                }
        if self.format_mode == "Audio only (mp3)":
            ydl_opts["postprocessors"].append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            )

        try:
            with ytdlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                title = info.get("title") if isinstance(info, dict) else None
                if title:
                    self.signals.title.emit(title)
                filename = ydl.prepare_filename(info)
                self.signals.finished.emit(True, filename)
        except Exception as exc:
            self.signals.log.emit(f"Error: {exc}")
            self.signals.finished.emit(False, "")


