from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QWidget, QFrame

from programs.config import CHECKMARK_ICON_PATH, RED_X_ICON_PATH, QUESTION_MARK_ICON_PATH

APP_DARK_THEME = """
QWidget {
    background-color: #0f141b;
    color: #d6dee8;
}
QDialog, QMessageBox, QInputDialog {
    font-size: 16px;
}
QDialog QLabel, QMessageBox QLabel, QInputDialog QLabel {
    font-size: 16px;
}
QDialog QPushButton, QMessageBox QPushButton, QInputDialog QPushButton {
    font-size: 15px;
    min-height: 38px;
    padding: 8px 12px;
}
QDialog QLineEdit, QInputDialog QLineEdit {
    font-size: 16px;
    min-height: 38px;
    padding: 6px 10px;
}
QDialog QListWidget {
    font-size: 15px;
}
QFrame#serviceCard {
    background-color: #1b2430;
    border: 1px solid #2e3f53;
    border-radius: 10px;
}
QLabel#serviceTitle {
    font-size: 14px;
    font-weight: 700;
    color: #eaf2ff;
}
QPushButton {
    background-color: #202b38;
    color: #d6dee8;
    border: 1px solid #2f4155;
    border-radius: 6px;
    padding: 7px 10px;
}
QPushButton:hover {
    background-color: #273545;
}
QPushButton:pressed {
    background-color: #1c2733;
}
QPushButton#serviceAction {
    background-color: #2f81f7;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 7px 12px;
    font-weight: 600;
}
QPushButton#serviceAction:hover {
    background-color: #4091ff;
}
QPushButton#serviceAction:pressed {
    background-color: #226ad1;
}
QPushButton#serviceAction[installed="true"] {
    background-color: #2ea043;
    border: 1px solid #3fb950;
    font-weight: 700;
}
QPushButton#serviceAction[installed="true"]:hover {
    background-color: #36b24d;
}
QLabel#syncStatusLabel {
    background-color: #16272f;
    color: #d8f4ff;
    border: 2px solid #35c8ff;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 700;
    padding: 8px 14px;
    letter-spacing: 0.6px;
}
QListWidget {
    background-color: #111923;
    border: 1px solid #2f4155;
    border-radius: 8px;
}
QFrame#backButtonCard {
    background-color: #991212;
    border-radius: 5px;
}
QFrame#backButtonCard:hover {
    background-color: #ba1616;
}
QLabel#backButtonLabel, QPushButton#backButtonArrow {
    background-color: transparent;
    color: #ffffff;
    font-weight: bold;
    border: none;
}
QFrame#pageHeader {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 #ff4fd8,
        stop: 0.33 #8b5cf6,
        stop: 0.66 #22c55e,
        stop: 1 #3b82f6
    );
    border: 1px solid #ffffff55;
    border-radius: 10px;
}
QFrame#pageHeaderSeparator {
    background-color: #ffffffdd;
    border: none;
}
"""

DEFAULT_WINDOW_WIDTH = 1440
DEFAULT_WINDOW_HEIGHT = 810
DEFAULT_MIN_WINDOW_WIDTH = 1280
DEFAULT_MIN_WINDOW_HEIGHT = 720
DEFAULT_DIALOG_WIDTH = 560
DEFAULT_DIALOG_HEIGHT = 640
DEFAULT_MIN_DIALOG_WIDTH = 500
DEFAULT_MIN_DIALOG_HEIGHT = 560


def apply_dark_theme(widget):
    widget.setStyleSheet(APP_DARK_THEME)


def configure_main_window(window):
    window.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
    window.setMinimumSize(DEFAULT_MIN_WINDOW_WIDTH, DEFAULT_MIN_WINDOW_HEIGHT)
    apply_dark_theme(window)


def configure_dialog(dialog, width=DEFAULT_DIALOG_WIDTH, height=DEFAULT_DIALOG_HEIGHT,
                     min_width=DEFAULT_MIN_DIALOG_WIDTH, min_height=DEFAULT_MIN_DIALOG_HEIGHT):
    dialog.resize(width, height)
    dialog.setMinimumSize(min_width, min_height)
    apply_dark_theme(dialog)


def create_page_header(back_button_container, title_text):
    header_container = QFrame()
    header_container.setObjectName("pageHeader")
    header_layout = QVBoxLayout(header_container)
    header_layout.setContentsMargins(10, 10, 10, 10)
    header_layout.setSpacing(8)

    title = QLabel(title_text)
    title.setAlignment(Qt.AlignCenter)
    title.setStyleSheet("font-size: 24px; font-weight: 800; color: #ffffff; background: transparent;")

    right_spacer = QWidget()
    right_spacer.setFixedSize(
        back_button_container.width(),
        back_button_container.height(),
    )
    right_spacer.setStyleSheet("background: transparent;")

    header_row = QHBoxLayout()
    header_row.addWidget(back_button_container)
    header_row.addStretch()
    header_row.addWidget(title)
    header_row.addStretch()
    header_row.addWidget(right_spacer)
    header_layout.addLayout(header_row)

    return header_container


def apply_status_icon(
    label,
    enabled,
    enabled_tooltip="Enabled",
    disabled_tooltip="Not enabled",
    unknown_tooltip="Unknown",
):
    if enabled is True:
        label.setPixmap(QPixmap(str(CHECKMARK_ICON_PATH)).scaled(20, 20))
        label.setToolTip(enabled_tooltip)
    elif enabled is False:
        label.setPixmap(QPixmap(str(RED_X_ICON_PATH)).scaled(20, 20))
        label.setToolTip(disabled_tooltip)
    else:
        label.setPixmap(QPixmap(str(QUESTION_MARK_ICON_PATH)).scaled(20, 20))
        label.setToolTip(unknown_tooltip)
