from __future__ import annotations

from typing import Callable, Optional, Any, Dict
from PySide6.QtCore import QObject, Signal, QThread
import yt_dlp as ytdlp
import os


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
    ) -> None:
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.format_mode = format_mode
        self.signals = DownloadSignals()

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
            speed = d.get("_speed_str") or ""
            eta = d.get("_eta_str") or ""
            self.signals.progress.emit(int(pct), speed, eta, "Downloading")
        elif d.get("status") == "finished":
            self.signals.log.emit("Merging/processing...")

    def run(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        ydl_opts: Dict[str, Any] = {
            "progress_hooks": [self._progress_hook],
            "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
            "noprogress": True,
            "ignoreerrors": True,
            "merge_output_format": "mp4",
            "format": self._select_format(),
            "postprocessors": [],
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


