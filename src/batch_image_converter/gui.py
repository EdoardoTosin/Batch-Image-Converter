"""PySide6 GUI for Batch Image Converter."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from . import __version__
from .constants import FILTER_NAMES
from .converter import ConversionConfig, ConversionResult, convert

# ── Worker thread ──────────────────────────────────────────────────────────────


class _Worker(QThread):
    log_line = Signal(str)
    progress_updated = Signal(int, int)  # completed, total
    finished = Signal(object)  # ConversionResult

    def __init__(self, cfg: ConversionConfig) -> None:
        super().__init__()
        self._cfg = cfg
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        result = convert(
            self._cfg,
            log=self.log_line.emit,
            progress=self.progress_updated.emit,
            is_cancelled=lambda: self._cancelled,
        )
        self.finished.emit(result)


# ── Main window ────────────────────────────────────────────────────────────────


class _MainWindow(QMainWindow):
    _DEFAULTS = dict(
        dpi=72,
        size=1000,
        quality=80,
        filter_idx=0,
        max_mpx=0.0,
        colorspace=False,
        optimize=True,
        alert=False,
    )

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Batch Image Converter")
        self.setMinimumSize(560, 520)
        self._worker: _Worker | None = None
        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.setCentralWidget(scroll)

        root = QWidget()
        scroll.setWidget(root)

        layout = QVBoxLayout(root)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        layout.addWidget(self._build_dirs_group())
        layout.addWidget(self._build_settings_group())
        layout.addWidget(self._build_options_group())
        layout.addLayout(self._build_buttons())
        layout.addWidget(self._build_progress())
        layout.addWidget(self._build_log_group(), stretch=1)

    def _build_dirs_group(self) -> QGroupBox:
        group = QGroupBox("Directories")
        form = QFormLayout(group)

        # Input row
        in_row = QHBoxLayout()
        self._path_edit = QLineEdit(str(Path.cwd()))
        self._path_edit.setPlaceholderText("Source directory…")
        in_btn = QPushButton("Browse…")
        in_btn.setFixedWidth(80)
        in_btn.clicked.connect(self._browse_input)
        in_row.addWidget(self._path_edit)
        in_row.addWidget(in_btn)
        form.addRow("Input:", in_row)

        # Output row
        out_row = QHBoxLayout()
        self._out_edit = QLineEdit()
        self._out_edit.setPlaceholderText("Leave empty for in-place conversion")
        out_btn = QPushButton("Browse…")
        out_btn.setFixedWidth(80)
        out_btn.clicked.connect(self._browse_output)
        out_row.addWidget(self._out_edit)
        out_row.addWidget(out_btn)
        form.addRow("Output:", out_row)

        return group

    def _build_settings_group(self) -> QGroupBox:
        group = QGroupBox("Image Settings")
        form = QFormLayout(group)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        self._dpi_spin = QSpinBox()
        self._dpi_spin.setRange(1, 1000)
        self._dpi_spin.setValue(self._DEFAULTS["dpi"])
        self._dpi_spin.setSuffix(" dpi")
        form.addRow("DPI:", self._dpi_spin)

        self._size_spin = QSpinBox()
        self._size_spin.setRange(1, 10000)
        self._size_spin.setValue(self._DEFAULTS["size"])
        self._size_spin.setSuffix(" px")
        self._size_spin.setToolTip(
            "Longest side - images are only downscaled, never upscaled."
        )
        form.addRow("Max dimension:", self._size_spin)

        self._quality_spin = QSpinBox()
        self._quality_spin.setRange(1, 100)
        self._quality_spin.setValue(self._DEFAULTS["quality"])
        self._quality_spin.setToolTip("Applies to JPEG output only.")
        form.addRow("JPEG quality:", self._quality_spin)

        self._filter_combo = QComboBox()
        for idx, name in FILTER_NAMES.items():
            self._filter_combo.addItem(f"{idx} – {name}", userData=idx)
        self._filter_combo.setCurrentIndex(self._DEFAULTS["filter_idx"])
        form.addRow("Resample filter:", self._filter_combo)

        self._mpx_spin = QDoubleSpinBox()
        self._mpx_spin.setRange(0, 10000)
        self._mpx_spin.setValue(self._DEFAULTS["max_mpx"])
        self._mpx_spin.setDecimals(1)
        self._mpx_spin.setSpecialValueText("Unlimited")
        self._mpx_spin.setToolTip(
            "Refuse to open inputs larger than this. 0 = no limit."
        )
        form.addRow("Max input megapixels:", self._mpx_spin)

        return group

    def _build_options_group(self) -> QGroupBox:
        group = QGroupBox("Options")
        h = QHBoxLayout(group)

        self._colorspace_cb = QCheckBox("CMYK→RGB (ICC)")
        self._colorspace_cb.setToolTip(
            "Use ICC profiles for CMYK → RGB conversion. "
            "Falls back to a simple conversion when profiles are not found."
        )
        self._colorspace_cb.setChecked(self._DEFAULTS["colorspace"])

        self._optimize_cb = QCheckBox("Optimise")
        self._optimize_cb.setToolTip(
            "Enable palette optimisation for JPEG and PNG output."
        )
        self._optimize_cb.setChecked(self._DEFAULTS["optimize"])

        self._alert_cb = QCheckBox("Alert when done")
        self._alert_cb.setToolTip("Play a system beep when conversion finishes.")
        self._alert_cb.setChecked(self._DEFAULTS["alert"])

        h.addWidget(self._colorspace_cb)
        h.addWidget(self._optimize_cb)
        h.addWidget(self._alert_cb)
        h.addStretch()
        return group

    def _build_buttons(self) -> QHBoxLayout:
        h = QHBoxLayout()

        self._convert_btn = QPushButton("Convert")
        self._convert_btn.setDefault(True)
        self._convert_btn.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self._convert_btn.clicked.connect(self._start)

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self._cancel_btn.clicked.connect(self._cancel)

        self._reset_btn = QPushButton("Reset")
        self._reset_btn.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self._reset_btn.clicked.connect(self._reset)

        h.addWidget(self._convert_btn)
        h.addWidget(self._cancel_btn)
        h.addStretch()
        h.addWidget(self._reset_btn)
        return h

    def _build_progress(self) -> QProgressBar:
        self._progress = QProgressBar()
        self._progress.setVisible(False)
        self._progress.setTextVisible(True)
        return self._progress

    def _build_log_group(self) -> QGroupBox:
        group = QGroupBox("Log")
        v = QVBoxLayout(group)
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMinimumHeight(160)
        mono = QFont("Courier New" if sys.platform == "win32" else "Monospace")
        mono.setStyleHint(QFont.StyleHint.Monospace)
        self._log.setFont(mono)
        v.addWidget(self._log)
        return group

    # ── Slots ──────────────────────────────────────────────────────────────

    def _browse_input(self) -> None:
        d = QFileDialog.getExistingDirectory(
            self, "Select input directory", self._path_edit.text()
        )
        if d:
            self._path_edit.setText(d)

    def _browse_output(self) -> None:
        start = self._out_edit.text() or self._path_edit.text()
        d = QFileDialog.getExistingDirectory(self, "Select output directory", start)
        if d:
            self._out_edit.setText(d)

    def _build_config(self) -> ConversionConfig | None:
        input_path = Path(self._path_edit.text().strip())
        if not input_path.is_dir():
            QMessageBox.warning(
                self, "Invalid input directory", f"Not a directory:\n{input_path}"
            )
            return None

        out_text = self._out_edit.text().strip()
        output_path = Path(out_text) if out_text else None

        if output_path is not None and output_path == input_path:
            output_path = None  # treat as in-place

        return ConversionConfig(
            path=input_path,
            output_path=output_path,
            dpi=self._dpi_spin.value(),
            size=self._size_spin.value(),
            filter=self._filter_combo.currentData(),
            quality=self._quality_spin.value(),
            max_megapixels=self._mpx_spin.value(),
            colorspace=self._colorspace_cb.isChecked(),
            optimize=self._optimize_cb.isChecked(),
        )

    def _start(self) -> None:
        cfg = self._build_config()
        if cfg is None:
            return

        if cfg.output_path is None:
            reply = QMessageBox.warning(
                self,
                "In-place conversion",
                "No output directory is set.\n\n"
                "Every image will be converted in-place:\n"
                "  • Originals are overwritten with the converted file.\n"
                "  • If the format changes (e.g. TIFF → JPEG), the original\n"
                "    file is permanently deleted - this cannot be undone.\n\n"
                "Back up your files before continuing.",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if reply != QMessageBox.StandardButton.Ok:
                return

        self._log.clear()
        self._progress.setValue(0)
        self._progress.setVisible(True)
        self._convert_btn.setEnabled(False)
        self._cancel_btn.setEnabled(True)

        self._worker = _Worker(cfg)
        self._worker.log_line.connect(self._append_log)
        self._worker.progress_updated.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _cancel(self) -> None:
        if self._worker:
            self._worker.cancel()
        self._cancel_btn.setEnabled(False)

    def _append_log(self, msg: str) -> None:
        self._log.appendPlainText(msg)
        self._log.moveCursor(QTextCursor.MoveOperation.End)

    def _on_progress(self, done: int, total: int) -> None:
        self._progress.setMaximum(total)
        self._progress.setValue(done)
        self._progress.setFormat(f"{done} / {total}")

    def _on_finished(self, result: ConversionResult) -> None:
        self._convert_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        self._progress.setVisible(False)

        self._append_log(
            f"\nDone - {result.converted} converted, "
            f"{result.failed} failed in {result.elapsed:.1f}s"
        )

        if self._alert_cb.isChecked():
            QApplication.beep()

        icon = (
            QMessageBox.Icon.Warning if result.failed else QMessageBox.Icon.Information
        )
        QMessageBox(
            icon,
            "Conversion complete",
            f"{result.converted} image(s) converted.\n{result.failed} failed.",
            parent=self,
        ).exec()

    def _reset(self) -> None:
        self._path_edit.setText(str(Path.cwd()))
        self._out_edit.clear()
        self._dpi_spin.setValue(self._DEFAULTS["dpi"])
        self._size_spin.setValue(self._DEFAULTS["size"])
        self._quality_spin.setValue(self._DEFAULTS["quality"])
        self._filter_combo.setCurrentIndex(self._DEFAULTS["filter_idx"])
        self._mpx_spin.setValue(self._DEFAULTS["max_mpx"])
        self._colorspace_cb.setChecked(self._DEFAULTS["colorspace"])
        self._optimize_cb.setChecked(self._DEFAULTS["optimize"])
        self._alert_cb.setChecked(self._DEFAULTS["alert"])
        self._log.clear()
        self._progress.setVisible(False)


# ── Public entry point ─────────────────────────────────────────────────────────


def launch() -> None:
    """Launch the GUI application."""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Batch Image Converter")
    app.setApplicationVersion(__version__)
    app.setStyle("Fusion")

    window = _MainWindow()
    window.resize(700, 740)
    window.show()

    screen = app.primaryScreen().availableGeometry()
    window.move(
        (screen.width() - window.width()) // 2,
        (screen.height() - window.height()) // 2,
    )

    sys.exit(app.exec())
