#!/usr/bin/env python3
"""Small PyQt6 GUI for the WTACMI recorder."""

import os
import sys
import traceback
from types import SimpleNamespace

from PyQt6.QtCore import QSettings, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

try:
    from wtacmi_recorder import DEFAULT_BASE_URL, benchmark_telemetry_rate, default_output_path, run_recording
except ImportError:
    from recorder.wtacmi_recorder import DEFAULT_BASE_URL, benchmark_telemetry_rate, default_output_path, run_recording


class RecorderThread(QThread):
    log_line = pyqtSignal(str)
    finished_with_status = pyqtSignal(bool, str)

    def __init__(self, args):
        super().__init__()
        self.args = args
        self._stop_requested = False

    def request_stop(self):
        self._stop_requested = True

    def run(self):
        try:
            run_recording(self.args, should_stop=lambda: self._stop_requested, log=self.log_line.emit)
            self.finished_with_status.emit(True, os.path.abspath(self.args.output))
        except Exception:
            self.finished_with_status.emit(False, traceback.format_exc())


class BenchmarkThread(QThread):
    log_line = pyqtSignal(str)
    finished_with_result = pyqtSignal(bool, object)

    def __init__(self, base_url, timeout, duration):
        super().__init__()
        self.base_url = base_url
        self.timeout = timeout
        self.duration = duration

    def run(self):
        try:
            self.log_line.emit("Detecting localhost 8111 polling rate...")
            result = benchmark_telemetry_rate(self.base_url, self.timeout, self.duration)
            self.finished_with_result.emit(True, result)
        except Exception:
            self.finished_with_result.emit(False, traceback.format_exc())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recorder_thread = None
        self.benchmark_thread = None
        self.settings = QSettings("WTACMI", "Recorder")
        self.setWindowTitle("WTACMI Recorder")
        self.resize(760, 560)

        self.controls_edit = QLineEdit()
        self.output_edit = QLineEdit(default_output_path())
        self.pilot_edit = QLineEdit("pilot")
        self.base_url_edit = QLineEdit(DEFAULT_BASE_URL)

        self.telemetry_hz = QDoubleSpinBox()
        self.telemetry_hz.setRange(1.0, 120.0)
        self.telemetry_hz.setDecimals(1)
        self.telemetry_hz.setValue(10.0)

        self.input_hz = QDoubleSpinBox()
        self.input_hz.setRange(1.0, 240.0)
        self.input_hz.setDecimals(1)
        self.input_hz.setValue(60.0)

        self.timeout = QDoubleSpinBox()
        self.timeout.setRange(0.05, 5.0)
        self.timeout.setDecimals(2)
        self.timeout.setValue(0.25)

        self.duration = QDoubleSpinBox()
        self.duration.setRange(0.0, 24 * 60 * 60.0)
        self.duration.setDecimals(1)
        self.duration.setValue(0.0)
        self.duration.setSuffix(" s")

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.detect_button = QPushButton("Detect Max Hz")
        self.stop_button.setEnabled(False)

        self._build_layout()
        self._connect_signals()
        self.load_settings()

    def _build_layout(self):
        controls_button = QPushButton("Browse...")
        controls_button.clicked.connect(self.choose_controls)
        output_button = QPushButton("Browse...")
        output_button.clicked.connect(self.choose_output)

        controls_row = QHBoxLayout()
        controls_row.addWidget(self.controls_edit)
        controls_row.addWidget(controls_button)

        output_row = QHBoxLayout()
        output_row.addWidget(self.output_edit)
        output_row.addWidget(output_button)

        form = QFormLayout()
        form.addRow("Controls .blk", controls_row)
        form.addRow("Output .acmi", output_row)
        form.addRow("Pilot", self.pilot_edit)
        form.addRow("8111 Base URL", self.base_url_edit)
        telemetry_row = QHBoxLayout()
        telemetry_row.addWidget(self.telemetry_hz)
        telemetry_row.addWidget(self.detect_button)
        form.addRow("Telemetry Hz", telemetry_row)
        form.addRow("Input Hz", self.input_hz)
        form.addRow("HTTP Timeout", self.timeout)
        form.addRow("Duration", self.duration)

        group = QGroupBox("Recording")
        group.setLayout(form)

        actions = QHBoxLayout()
        actions.addWidget(self.start_button)
        actions.addWidget(self.stop_button)
        actions.addStretch(1)

        note = QLabel("Duration 0 means record until Stop. Start War Thunder before recording.")
        note.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(group)
        layout.addLayout(actions)
        layout.addWidget(note)
        layout.addWidget(self.log, 1)

        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)

    def _connect_signals(self):
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.detect_button.clicked.connect(self.detect_polling_rate)

    def load_settings(self):
        self.controls_edit.setText(self.settings.value("controls", "", str))
        self.output_edit.setText(self.settings.value("output", self.output_edit.text(), str))
        self.pilot_edit.setText(self.settings.value("pilot", "pilot", str))
        self.base_url_edit.setText(self.settings.value("baseUrl", DEFAULT_BASE_URL, str))
        self.telemetry_hz.setValue(float(self.settings.value("telemetryHz", 10.0)))
        self.input_hz.setValue(float(self.settings.value("inputHz", 60.0)))
        self.timeout.setValue(float(self.settings.value("timeout", 0.25)))
        self.duration.setValue(float(self.settings.value("duration", 0.0)))

    def save_settings(self):
        self.settings.setValue("controls", self.controls_edit.text().strip())
        self.settings.setValue("output", self.output_edit.text().strip())
        self.settings.setValue("pilot", self.pilot_edit.text().strip() or "pilot")
        self.settings.setValue("baseUrl", self.base_url_edit.text().strip() or DEFAULT_BASE_URL)
        self.settings.setValue("telemetryHz", self.telemetry_hz.value())
        self.settings.setValue("inputHz", self.input_hz.value())
        self.settings.setValue("timeout", self.timeout.value())
        self.settings.setValue("duration", self.duration.value())
        self.settings.sync()

    def choose_controls(self):
        default_dir = os.path.expanduser(r"~/Documents/My Games/WarThunder/Saves")
        path, _ = QFileDialog.getOpenFileName(self, "Select War Thunder controls file", default_dir, "War Thunder controls (*.blk);;All files (*)")
        if path:
            self.controls_edit.setText(path)
            self.save_settings()

    def choose_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save ACMI recording", self.output_edit.text(), "ACMI recording (*.acmi);;All files (*)")
        if path:
            if not path.lower().endswith(".acmi"):
                path += ".acmi"
            self.output_edit.setText(path)
            self.save_settings()

    def append_log(self, text):
        self.log.appendPlainText(text)

    def build_args(self):
        controls = self.controls_edit.text().strip()
        output = self.output_edit.text().strip()
        if not controls:
            raise ValueError("Select a War Thunder controls .blk file.")
        if not os.path.isfile(controls):
            raise ValueError(f"Controls file does not exist:\n{controls}")
        if not output:
            raise ValueError("Choose an output .acmi file.")
        if not output.lower().endswith(".acmi"):
            output += ".acmi"
            self.output_edit.setText(output)
        return SimpleNamespace(
            controls=controls,
            output=output,
            pilot=self.pilot_edit.text().strip() or "Pilot",
            base_url=self.base_url_edit.text().strip() or DEFAULT_BASE_URL,
            telemetry_hz=float(self.telemetry_hz.value()),
            input_hz=float(self.input_hz.value()),
            timeout=float(self.timeout.value()),
            duration=float(self.duration.value()),
        )

    def start_recording(self):
        try:
            args = self.build_args()
        except ValueError as exc:
            QMessageBox.warning(self, "Cannot start recording", str(exc))
            return

        self.save_settings()
        self.log.clear()
        self.recorder_thread = RecorderThread(args)
        self.recorder_thread.log_line.connect(self.append_log)
        self.recorder_thread.finished_with_status.connect(self.recording_finished)
        self.recorder_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.detect_button.setEnabled(False)
        self.append_log("Recording started.")

    def stop_recording(self):
        if self.recorder_thread:
            self.append_log("Stop requested. Finalizing package...")
            self.recorder_thread.request_stop()
            self.stop_button.setEnabled(False)

    def recording_finished(self, ok, message):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.detect_button.setEnabled(True)
        self.recorder_thread = None
        if ok:
            self.append_log(f"Recording saved: {message}")
            QMessageBox.information(self, "Recording saved", message)
        else:
            self.append_log(message)
            QMessageBox.critical(self, "Recording failed", message)

    def detect_polling_rate(self):
        if self.recorder_thread and self.recorder_thread.isRunning():
            QMessageBox.warning(self, "Recorder is running", "Stop recording before detecting polling rate.")
            return
        if self.benchmark_thread and self.benchmark_thread.isRunning():
            return
        self.save_settings()
        self.detect_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.benchmark_thread = BenchmarkThread(
            self.base_url_edit.text().strip() or DEFAULT_BASE_URL,
            float(self.timeout.value()),
            3.0,
        )
        self.benchmark_thread.log_line.connect(self.append_log)
        self.benchmark_thread.finished_with_result.connect(self.polling_rate_detected)
        self.benchmark_thread.start()

    def polling_rate_detected(self, ok, result):
        self.benchmark_thread = None
        self.detect_button.setEnabled(True)
        self.start_button.setEnabled(True)
        if not ok:
            self.append_log(str(result))
            QMessageBox.critical(self, "Detection failed", str(result))
            return

        recommended = float(result["recommendedHz"])
        self.telemetry_hz.setValue(recommended)
        self.save_settings()
        self.append_log(
            "Polling detection complete: "
            f"full-cycle {result['fullCycleHz']} Hz, "
            f"successful {result['successfulCycleHz']} Hz, "
            f"avg cycle {result['avgCycleMs']} ms, "
            f"p95 cycle {result['p95CycleMs']} ms, "
            f"recommended {recommended} Hz."
        )
        for name, endpoint in result["endpoints"].items():
            self.append_log(
                f"  {name}: avg {endpoint['avgLatencyMs']} ms, "
                f"max {endpoint['maxLatencyMs']} ms, errors {endpoint['errors']}"
            )
        if result["successfulCycles"] == 0:
            QMessageBox.warning(
                self,
                "No successful cycles",
                "No complete 8111 polling cycle succeeded. Start War Thunder and try again.",
            )

    def closeEvent(self, event):
        self.save_settings()
        if self.recorder_thread and self.recorder_thread.isRunning():
            self.stop_recording()
            self.recorder_thread.wait(5000)
        if self.benchmark_thread and self.benchmark_thread.isRunning():
            self.benchmark_thread.wait(5000)
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
