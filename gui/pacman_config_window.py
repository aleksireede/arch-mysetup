import subprocess
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QLabel,
    QFrame,
)

try:
    from .ui_helpers import create_back_button
    from .theme import apply_dark_theme, create_page_header, apply_status_icon
except ImportError:
    from ui_helpers import create_back_button
    from theme import apply_dark_theme, create_page_header, apply_status_icon

from scripts.extra import reflector_service_timer
from programs.text_editor import enable_multilib, pacman_enable_color, check_multilib, check_pacman_color
from programs.config import PACMAN_REFLECTOR_CONFIG_PATH


class PacmanConfigWindow(QMainWindow):
    PAGE_BUTTON_WIDTH = 300

    def __init__(self, advanced_window=None):
        super().__init__()
        self.advanced_window = advanced_window
        self.status_labels = {}
        self.tweaks = []
        self.back_button_container = None

        self.setWindowTitle("Pacman Config")
        self.setGeometry(100, 100, 900, 600)
        self.setMinimumSize(860, 560)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        apply_dark_theme(self)
        layout = QVBoxLayout(central)

        self.back_button_container, _, _, _ = create_back_button(self.go_back)
        header_widget = create_page_header(self.back_button_container, "Pacman Config")

        self.tweaks = [
            ("multilib", "Enable Pacman Multilib", enable_multilib, "Multilib enable task completed.", self.safe_check_multilib),
            ("pacman_color", "Enable Pacman Color", pacman_enable_color, "Pacman color enable task completed.", self.safe_check_pacman_color),
            ("reflector", "Enable Reflector Timer", reflector_service_timer, "Reflector timer task completed.", self.is_reflector_enabled),
        ]

        container = QFrame()
        container_layout = QVBoxLayout(container)

        for key, label, callback, success, _ in self.tweaks:
            row_layout = QHBoxLayout()
            button = QPushButton(label)
            button.setFixedWidth(self.PAGE_BUTTON_WIDTH)
            button.clicked.connect(lambda _, cb=callback, msg=success: self.run_tweak(cb, msg))
            status_label = QLabel()
            status_label.setMinimumWidth(24)
            status_label.setMaximumWidth(24)
            row_layout.addStretch()
            row_layout.addWidget(button)
            row_layout.addWidget(status_label)
            row_layout.addStretch()
            container_layout.addLayout(row_layout)
            self.status_labels[key] = status_label

        container_layout.addStretch()

        layout.addWidget(header_widget)
        layout.addSpacing(12)
        layout.addWidget(container)
        self.refresh_statuses()

    def go_back(self):
        if self.advanced_window:
            self.advanced_window.refresh_statuses()
            self.advanced_window.show()
        self.hide()

    def run_tweak(self, callback, success_message):
        try:
            callback()
            QMessageBox.information(self, "Done", success_message)
            self.refresh_statuses()
        except subprocess.CalledProcessError as e:
            if e.returncode == 126:
                QMessageBox.critical(self, "Authentication Failed", "Authentication failed.")
            else:
                QMessageBox.critical(self, "Error", f"Action failed: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Action failed: {e}")

    def safe_check_multilib(self):
        try:
            return check_multilib()
        except Exception:
            return None

    def safe_check_pacman_color(self):
        try:
            return check_pacman_color()
        except Exception:
            return None

    def is_reflector_enabled(self):
        return PACMAN_REFLECTOR_CONFIG_PATH.exists()

    def set_status_icon(self, label: QLabel, enabled):
        apply_status_icon(label, enabled)

    def refresh_statuses(self):
        for key, _, _, _, status_fn in self.tweaks:
            label = self.status_labels.get(key)
            if label is None:
                continue
            try:
                enabled = status_fn()
            except Exception:
                enabled = None
            self.set_status_icon(label, enabled)
