from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QLabel,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTextEdit,
)

from utils.settings import AppSettings
from downloader.worker import DownloadWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Youtube Downloader (yt-dlp)")
        self.resize(1000, 700)

        self.settings = AppSettings.load()
        self.current_worker: DownloadWorker | None = None
        self.active_row: int | None = None

        self._build_menu()
        self._build_ui()
        self._apply_theme(self.settings.theme)

    def _build_menu(self) -> None:
        menubar = self.menuBar()
        view_menu = menubar.addMenu("View")
        self.toggle_theme_action = QAction("Toggle Theme", self)
        self.toggle_theme_action.triggered.connect(self._on_toggle_theme)
        view_menu.addAction(self.toggle_theme_action)

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # URL row
        url_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube/playlist URLs, one per line")
        self.add_button = QPushButton("Add to Queue")
        self.add_button.clicked.connect(self._on_add_to_queue)
        url_row.addWidget(self.url_input, 3)
        url_row.addWidget(self.add_button, 1)
        root.addLayout(url_row)

        # Options row
        options_row = QHBoxLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Best (video+audio)",
            "Audio only (m4a)",
            "Audio only (mp3)",
            "Best video only",
        ])
        self.dest_label = QLabel("Output directory:")
        self.dest_value = QLineEdit()
        self.dest_value.setReadOnly(True)
        self.dest_value.setText(self.settings.output_dir or "")
        self.browse_button = QPushButton("Browse…")
        self.browse_button.clicked.connect(self._on_browse)
        options_row.addWidget(self.format_combo, 1)
        options_row.addWidget(self.dest_label)
        options_row.addWidget(self.dest_value, 2)
        options_row.addWidget(self.browse_button)
        root.addLayout(options_row)

        # Queue table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["URL", "Title", "Progress", "Speed", "ETA", "Status"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        root.addWidget(self.table)

        # Controls row
        controls = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.clear_button = QPushButton("Clear")
        self.pause_button.setEnabled(False)
        controls.addWidget(self.start_button)
        controls.addWidget(self.pause_button)
        controls.addWidget(self.clear_button)
        controls.addStretch(1)
        root.addLayout(controls)

        # Logs
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        root.addWidget(self.logs)

        # Wire actions
        self.start_button.clicked.connect(self._on_start)
        self.clear_button.clicked.connect(self._on_clear)

    def _apply_theme(self, theme: str) -> None:
        if theme == "dark":
            self.setStyleSheet(
                """
                QWidget { background: #121212; color: #e0e0e0; }
                QLineEdit, QTextEdit, QComboBox { background: #1e1e1e; border: 1px solid #333; }
                QPushButton { background: #2a2a2a; border: 1px solid #444; padding: 6px 12px; }
                QTableWidget { background: #1a1a1a; }
                """
            )
        else:
            self.setStyleSheet("")

    def _on_toggle_theme(self) -> None:
        new_theme = "dark" if self.settings.theme != "dark" else "light"
        self.settings.theme = new_theme
        self.settings.save()
        self._apply_theme(new_theme)

    def _on_browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select output directory")
        if path:
            self.dest_value.setText(path)
            self.settings.output_dir = path
            self.settings.save()

    def _on_add_to_queue(self) -> None:
        text = self.url_input.text().strip()
        if not text:
            return
        urls = [u.strip() for u in text.splitlines() if u.strip()]
        for url in urls:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(url))
            self.table.setItem(row, 1, QTableWidgetItem(""))
            self.table.setItem(row, 2, QTableWidgetItem("0%"))
            self.table.setItem(row, 3, QTableWidgetItem("-"))
            self.table.setItem(row, 4, QTableWidgetItem("-"))
            self.table.setItem(row, 5, QTableWidgetItem("Queued"))
        self.url_input.clear()

    # Download flow
    def _find_next_queued_row(self) -> int | None:
        for row in range(self.table.rowCount()):
            status_item = self.table.item(row, 5)
            if status_item and status_item.text() in ("Queued", "Error"):
                return row
        return None

    def _on_start(self) -> None:
        if self.current_worker is not None:
            return
        if not self.dest_value.text():
            self.logs.append("Please select an output directory.")
            return
        next_row = self._find_next_queued_row()
        if next_row is None:
            self.logs.append("No queued items.")
            return
        self._start_row_download(next_row)

    def _start_row_download(self, row: int) -> None:
        url = self.table.item(row, 0).text()
        fmt = self.format_combo.currentText()
        out_dir = self.dest_value.text()

        worker = DownloadWorker(url=url, output_dir=out_dir, format_mode=fmt)
        self.current_worker = worker
        self.active_row = row

        self.table.setItem(row, 5, QTableWidgetItem("Downloading"))

        worker.signals.title.connect(lambda title: self._on_title(row, title))
        worker.signals.progress.connect(lambda pct, speed, eta, status: self._on_progress(row, pct, speed, eta, status))
        worker.signals.log.connect(self.logs.append)
        worker.signals.finished.connect(lambda ok, path: self._on_finished(row, ok, path))
        worker.start()

    def _on_title(self, row: int, title: str) -> None:
        self.table.setItem(row, 1, QTableWidgetItem(title))

    def _on_progress(self, row: int, percent: int, speed: str, eta: str, status: str) -> None:
        self.table.setItem(row, 2, QTableWidgetItem(f"{percent}%"))
        self.table.setItem(row, 3, QTableWidgetItem(speed or "-"))
        self.table.setItem(row, 4, QTableWidgetItem(eta or "-"))
        self.table.setItem(row, 5, QTableWidgetItem(status or "Downloading"))

    def _on_finished(self, row: int, ok: bool, path: str) -> None:
        self.table.setItem(row, 5, QTableWidgetItem("Completed" if ok else "Error"))
        self.current_worker = None
        self.active_row = None
        # Auto-continue next item
        next_row = self._find_next_queued_row()
        if next_row is not None:
            self._start_row_download(next_row)

    def _on_clear(self) -> None:
        # remove rows that are Completed or Error
        rows_to_remove = []
        for row in range(self.table.rowCount()):
            status = self.table.item(row, 5)
            if status and status.text() in ("Completed", "Error"):
                rows_to_remove.append(row)
        for idx in reversed(rows_to_remove):
            self.table.removeRow(idx)


