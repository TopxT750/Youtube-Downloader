import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication
from ui.main_window import MainWindow


def main() -> int:
    QCoreApplication.setOrganizationName("YoutubeDownloader")
    QCoreApplication.setApplicationName("YoutubeDownloader")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


