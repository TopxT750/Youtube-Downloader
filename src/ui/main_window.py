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
    QProgressBar,
)

from utils.settings import AppSettings
from downloader.worker import DownloadWorker
from PySide6.QtWidgets import QDialog, QFormLayout, QCheckBox, QSpinBox, QComboBox
from utils.aria2 import ensure_aria2c


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Youtube Downloader (yt-dlp)")
        self.resize(1000, 700)

        self.settings = AppSettings.load()
        self.current_worker: DownloadWorker | None = None
        self.active_row: int | None = None
        self.advanced_options: dict | None = None

        self._build_menu()
        self._build_ui()
        self._apply_theme(self.settings.theme)

    def _build_menu(self) -> None:
        menubar = self.menuBar()
        view_menu = menubar.addMenu("View")
        self.toggle_theme_action = QAction("Toggle Theme", self)
        self.toggle_theme_action.triggered.connect(self._on_toggle_theme)
        view_menu.addAction(self.toggle_theme_action)

        settings_menu = menubar.addMenu("Settings")
        self.download_settings_action = QAction("Download Settings…", self)
        self.download_settings_action.triggered.connect(self._on_open_download_settings)
        settings_menu.addAction(self.download_settings_action)

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

        # Load default downloads folder from settings if present
        if self.settings.output_dir:
            self.dest_value.setText(self.settings.output_dir)

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
        self.power_button = QPushButton("Power Download…")
        self.pause_button.setEnabled(False)
        controls.addWidget(self.start_button)
        controls.addWidget(self.power_button)
        controls.addWidget(self.pause_button)
        controls.addWidget(self.clear_button)
        controls.addStretch(1)
        root.addLayout(controls)

        # Global progress bar
        self.overall_bar = QProgressBar()
        self.overall_bar.setRange(0, 100)
        self.overall_bar.setValue(0)
        self.overall_bar.setFormat("Overall: %p%")
        root.addWidget(self.overall_bar)

        # Logs
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setMaximumHeight(140)
        root.addWidget(self.logs)

        # Wire actions
        self.start_button.clicked.connect(self._on_start)
        self.clear_button.clicked.connect(self._on_clear)
        self.power_button.clicked.connect(self._on_open_power)

    def _apply_theme(self, theme: str) -> None:
        if theme == "dark":
            self.setStyleSheet(
                """
                QWidget { background: #0f1115; color: #e6e6e6; }
                QLineEdit, QTextEdit, QComboBox { background: #171a21; border: 1px solid #2a2f3a; border-radius: 6px; padding: 6px; }
                QPushButton { background: #222735; border: 1px solid #2f3545; border-radius: 6px; padding: 8px 14px; }
                QPushButton:hover { background: #2a3040; }
                QTableWidget { background: #141820; gridline-color: #2a2f3a; }
                QHeaderView::section { background: #141820; border: 0; padding: 6px; }
                QProgressBar { background: #171a21; border: 1px solid #2a2f3a; border-radius: 6px; text-align: center; }
                QProgressBar::chunk { background-color: #3a86ff; border-radius: 6px; }
                """
            )
        else:
            self.setStyleSheet("")

    def _on_toggle_theme(self) -> None:
        new_theme = "dark" if self.settings.theme != "dark" else "light"
        self.settings.theme = new_theme
        self.settings.save()
        self._apply_theme(new_theme)

    def _on_open_download_settings(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("Download Settings")
        layout = QFormLayout(dlg)

        aria2_chk = QCheckBox("Use Faster Engine (recommended)")
        aria2_chk.setToolTip("Uses a built-in advanced downloader (aria2c) to speed up downloads.")
        aria2_chk.setChecked(self.settings.use_aria2c)
        layout.addRow(aria2_chk)

        speed_label = QLabel("Speed mode")
        speed_combo = QComboBox()
        speed_combo.addItems(["Normal", "Faster", "Fastest"])
        # Map existing numeric setting to a selection
        current = int(self.settings.concurrent_fragments or 8)
        if current <= 4:
            speed_combo.setCurrentText("Normal")
        elif current <= 8:
            speed_combo.setCurrentText("Faster")
        else:
            speed_combo.setCurrentText("Fastest")
        speed_combo.setToolTip("Choose how aggressive the app should be to speed up downloads.")
        layout.addRow(speed_label, speed_combo)

        default_dir_label = QLabel("Default downloads folder")
        default_dir_btn = QPushButton("Choose…")
        default_dir_val = QLineEdit(self.settings.output_dir or "")
        default_dir_val.setReadOnly(True)
        def _pick_dir():
            path = QFileDialog.getExistingDirectory(self, "Select default downloads folder")
            if path:
                default_dir_val.setText(path)
        row = QHBoxLayout()
        row.addWidget(default_dir_val)
        row.addWidget(default_dir_btn)
        layout.addRow(default_dir_label, QWidget())
        layout.addRow(row)

        btns = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addRow(btns)

        default_dir_btn.clicked.connect(_pick_dir)
        cancel_btn.clicked.connect(dlg.reject)

        def _accept():
            self.settings.use_aria2c = aria2_chk.isChecked()
            # Map selection back to numeric fragments
            sel = speed_combo.currentText()
            if sel == "Normal":
                self.settings.concurrent_fragments = 4
            elif sel == "Faster":
                self.settings.concurrent_fragments = 8
            else:
                self.settings.concurrent_fragments = 16
            self.settings.output_dir = default_dir_val.text() or None
            self.settings.save()
            if self.settings.output_dir:
                self.dest_value.setText(self.settings.output_dir)
            if self.settings.use_aria2c:
                ensure_aria2c()
            dlg.accept()
        ok_btn.clicked.connect(_accept)

        dlg.exec()

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
            # Progress cell: bar + percent label aligned
            cell = QWidget()
            h = QHBoxLayout(cell)
            h.setContentsMargins(6, 2, 6, 2)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            pct = QLabel("0%")
            pct.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            h.addWidget(bar, 3)
            h.addWidget(pct, 1)
            self.table.setCellWidget(row, 2, cell)
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

        worker = DownloadWorker(url=url, output_dir=out_dir, format_mode=fmt, advanced_options=self.advanced_options)
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
        widget = self.table.cellWidget(row, 2)
        if isinstance(widget, QWidget):
            bar = widget.findChild(QProgressBar)
            label = widget.findChild(QLabel)
            if isinstance(bar, QProgressBar):
                bar.setValue(max(0, min(100, percent)))
            if isinstance(label, QLabel):
                label.setText(f"{max(0, min(100, percent))}%")
        self.table.setItem(row, 3, QTableWidgetItem(speed or "-"))
        self.table.setItem(row, 4, QTableWidgetItem(eta or "-"))
        self.table.setItem(row, 5, QTableWidgetItem(status or "Downloading"))
        # Update overall bar
        self._update_overall_progress()

    def _on_finished(self, row: int, ok: bool, path: str) -> None:
        self.table.setItem(row, 5, QTableWidgetItem("Completed" if ok else "Error"))
        self.current_worker = None
        self.active_row = None
        # Auto-continue next item
        next_row = self._find_next_queued_row()
        if next_row is not None:
            self._start_row_download(next_row)
        else:
            self._update_overall_progress()

    def _on_clear(self) -> None:
        # remove rows that are Completed or Error
        rows_to_remove = []
        for row in range(self.table.rowCount()):
            status = self.table.item(row, 5)
            if status and status.text() in ("Completed", "Error"):
                rows_to_remove.append(row)
        for idx in reversed(rows_to_remove):
            self.table.removeRow(idx)
        self._update_overall_progress()

    def _update_overall_progress(self) -> None:
        total = self.table.rowCount()
        if total == 0:
            self.overall_bar.setValue(0)
            return
        percents = []
        for row in range(total):
            widget = self.table.cellWidget(row, 2)
            if isinstance(widget, QWidget):
                bar = widget.findChild(QProgressBar)
                if isinstance(bar, QProgressBar):
                    percents.append(bar.value())
            else:
                percents.append(0)
        overall = int(sum(percents) / max(1, len(percents)))
        self.overall_bar.setValue(overall)

    def _on_open_power(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("Power Download")
        form = QFormLayout(dlg)
        # Container
        c_label = QLabel("Container (file type)")
        c_combo = QComboBox()
        c_combo.addItems(["mp4", "mkv", "webm"])
        form.addRow(c_label, c_combo)
        # Video quality
        vq_label = QLabel("Video quality")
        vq_combo = QComboBox()
        vq_combo.addItems(["Best", "1080p", "720p", "480p"])
        form.addRow(vq_label, vq_combo)
        # Audio quality (bitrate)
        aq_label = QLabel("Audio quality")
        aq_combo = QComboBox()
        aq_combo.addItems(["Best", "160k", "128k"])
        form.addRow(aq_label, aq_combo)

        buttons = QHBoxLayout()
        ok = QPushButton("Apply")
        cancel = QPushButton("Cancel")
        buttons.addWidget(ok)
        buttons.addWidget(cancel)
        form.addRow(buttons)

        cancel.clicked.connect(dlg.reject)

        def _apply():
            self.advanced_options = {
                "container": c_combo.currentText(),
                "video_quality": vq_combo.currentText(),
                "audio_quality": aq_combo.currentText(),
            }
            dlg.accept()
        ok.clicked.connect(_apply)
        dlg.exec()


