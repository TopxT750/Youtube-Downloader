import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication
from ui.main_window import MainWindow
from utils.ffmpeg import ensure_ffmpeg


def main() -> int:
    QCoreApplication.setOrganizationName("YoutubeDownloader")
    QCoreApplication.setApplicationName("YoutubeDownloader")

    app = QApplication(sys.argv)
    # Warm up ffmpeg (non-blocking UI creation still happens)
    try:
        ensure_ffmpeg()
    except Exception:
        pass
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


