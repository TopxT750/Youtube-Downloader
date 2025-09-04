from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


SETTINGS_FILE = Path.home() / ".ytdlp_gui_settings.json"


@dataclass
class AppSettings:
    theme: str = "light"
    output_dir: str | None = None
    use_aria2c: bool = False
    concurrent_fragments: int = 8

    @classmethod
    def load(cls) -> "AppSettings":
        if SETTINGS_FILE.exists():
            try:
                data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
                return cls(**data)
            except Exception:
                pass
        return cls()

    def save(self) -> None:
        try:
            SETTINGS_FILE.write_text(
                json.dumps(
                    {
                        "theme": self.theme,
                        "output_dir": self.output_dir,
                        "use_aria2c": self.use_aria2c,
                        "concurrent_fragments": self.concurrent_fragments,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except Exception:
            # Best-effort; ignore persistence errors for now
            pass


