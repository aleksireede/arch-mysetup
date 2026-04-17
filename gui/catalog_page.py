from pathlib import Path

from PyQt5.QtCore import QObject, QThread, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from programs.config import CHECKMARK_ICON_PATH, QUESTION_MARK_ICON_PATH, RED_X_ICON_PATH

try:
    from .ui_helpers import create_back_button
    from .theme import configure_main_window, create_page_header
except ImportError:
    from ui_helpers import create_back_button
    from theme import configure_main_window, create_page_header


class CatalogLoadWorker(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, load_function):
        super().__init__()
        self.load_function = load_function

    def run(self):
        try:
            self.finished.emit(self.load_function())
        except Exception as e:
            self.error.emit(str(e))


class CatalogActionWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, entry, action_function):
        super().__init__()
        self.entry = entry
        self.action_function = action_function

    def run(self):
        try:
            self.action_function(self.entry)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class CatalogPage(QMainWindow):
    ICON_SIZE = 72

    def __init__(self, setup_window, title, noun_plural, load_function, action_function):
        super().__init__()
        self.setup_window = setup_window
        self.page_title = title
        self.noun_plural = noun_plural
        self.load_function = load_function
        self.action_function = action_function
        self.thread = None
        self.worker = None
        self.action_thread = None
        self.action_worker = None
        self.current_entry = None
        self.refresh_button = None
        self.status_label = None
        self.cards_layout = None
        self.card_buttons = []
        self.back_button_container = None
        self.setWindowTitle(title)
        configure_main_window(self)
        self.init_ui()
        self.refresh_catalog_async()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.back_button_container, _, _, _ = create_back_button(self.go_back_to_setup)
        header_widget = create_page_header(self.back_button_container, self.page_title)

        self.status_label = QLabel(f"Loading {self.noun_plural.lower()}...")
        self.status_label.setObjectName("syncStatusLabel")

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setFixedWidth(200)
        self.refresh_button.clicked.connect(self.refresh_catalog_async)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        self.cards_layout = QVBoxLayout(scroll_content)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()
        scroll_area.setWidget(scroll_content)

        layout.addWidget(header_widget)
        layout.addSpacing(12)
        layout.addWidget(self.status_label)
        layout.addWidget(scroll_area)
        layout.addWidget(self.refresh_button, alignment=Qt.AlignmentFlag.AlignHCenter)

    def refresh_catalog_async(self):
        if self.thread and self.thread.isRunning():
            return

        self.set_controls_enabled(False)
        self.status_label.setText(f"Refreshing {self.noun_plural.lower()}...")
        self.clear_cards()

        self.thread = QThread()
        self.worker = CatalogLoadWorker(self.load_function)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_entries_loaded)
        self.worker.error.connect(self.on_entries_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.cleanup_thread)
        self.thread.start()

    def on_entries_loaded(self, entries):
        self.set_controls_enabled(True)
        self.status_label.setText(f"{self.noun_plural} are ready.")
        self.render_entries(entries)

    def on_entries_error(self, error_message):
        self.set_controls_enabled(True)
        self.status_label.setText(f"Could not load {self.noun_plural.lower()}: {error_message}")
        QMessageBox.critical(self, f"{self.page_title} Error", error_message)

    def cleanup_thread(self):
        self.thread = None
        self.worker = None

    def render_entries(self, entries):
        self.clear_cards()

        if not entries:
            empty_label = QLabel(f"No {self.noun_plural.lower()} found in the catalog.")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_layout.insertWidget(0, empty_label)
            return

        for entry in entries:
            card = QFrame()
            card.setObjectName("serviceCard")
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(16, 16, 16, 16)
            card_layout.setSpacing(16)

            icon_label = QLabel()
            icon_label.setFixedSize(self.ICON_SIZE, self.ICON_SIZE)
            icon_label.setScaledContents(True)
            icon_path = Path(entry.get("icon_path") or "")
            if not icon_path.exists():
                icon_path = QUESTION_MARK_ICON_PATH
            icon_label.setPixmap(QPixmap(str(icon_path)))

            info_layout = QVBoxLayout()
            title_label = QLabel(entry["title"])
            title_label.setObjectName("serviceTitle")
            description_label = QLabel(entry["description"])
            description_label.setWordWrap(True)
            description_label.setStyleSheet("color: rgba(255, 255, 255, 0.72);")

            status_row = QHBoxLayout()
            status_icon = QLabel()
            status_path = CHECKMARK_ICON_PATH if entry["installed"] else RED_X_ICON_PATH
            status_icon.setPixmap(QPixmap(str(status_path)).scaled(18, 18))
            status_label = QLabel("Installed" if entry["installed"] else "Not installed")
            status_row.addWidget(status_icon)
            status_row.addWidget(status_label)
            status_row.addStretch()

            info_layout.addWidget(title_label)
            info_layout.addWidget(description_label)
            info_layout.addLayout(status_row)

            action_button = QPushButton("Uninstall" if entry["installed"] else "Install")
            action_button.setObjectName("serviceAction")
            action_button.setFixedWidth(160)
            action_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            action_button.clicked.connect(
                lambda checked=False, current_entry=entry: self.start_catalog_action(current_entry)
            )
            self.card_buttons.append(action_button)

            card_layout.addWidget(icon_label)
            card_layout.addLayout(info_layout, 1)
            card_layout.addWidget(action_button)

            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    def clear_cards(self):
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        if self.cards_layout.count() == 1:
            item = self.cards_layout.itemAt(0)
            if item and item.widget() is not None and isinstance(item.widget(), QLabel):
                widget = self.cards_layout.takeAt(0).widget()
                widget.deleteLater()
        self.card_buttons = []

    def start_catalog_action(self, entry):
        if self.action_thread and self.action_thread.isRunning():
            return

        verb = "Uninstalling" if entry.get("installed") else "Installing"
        confirm = QMessageBox.question(
            self,
            f"{verb} {entry['title']}",
            f"{verb} {entry['title']}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        self.current_entry = entry
        self.set_controls_enabled(False)
        self.status_label.setText(f"{verb} {entry['title']}...")

        self.action_thread = QThread()
        self.action_worker = CatalogActionWorker(entry, self.action_function)
        self.action_worker.moveToThread(self.action_thread)
        self.action_thread.started.connect(self.action_worker.run)
        self.action_worker.finished.connect(self.on_catalog_action_finished)
        self.action_worker.error.connect(self.on_catalog_action_error)
        self.action_worker.finished.connect(self.action_thread.quit)
        self.action_worker.finished.connect(self.action_worker.deleteLater)
        self.action_worker.error.connect(self.action_thread.quit)
        self.action_worker.error.connect(self.action_worker.deleteLater)
        self.action_thread.finished.connect(self.action_thread.deleteLater)
        self.action_thread.finished.connect(self.cleanup_action_thread)
        self.action_thread.start()

    def on_catalog_action_finished(self):
        self.set_controls_enabled(True)
        self.status_label.setText(f"{self.page_title} action completed.")
        self.refresh_catalog_async()

    def on_catalog_action_error(self, error_message):
        self.set_controls_enabled(True)
        self.status_label.setText(f"{self.page_title} action failed: {error_message}")
        QMessageBox.critical(self, f"{self.page_title} Action Error", error_message)
        self.refresh_catalog_async()

    def cleanup_action_thread(self):
        self.action_thread = None
        self.action_worker = None
        self.current_entry = None

    def set_controls_enabled(self, enabled):
        self.refresh_button.setEnabled(enabled)
        for button in self.card_buttons:
            button.setEnabled(enabled)

    def go_back_to_setup(self):
        if self.setup_window:
            self.setup_window.show()
        self.hide()

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(3000)
        if self.action_thread and self.action_thread.isRunning():
            self.action_thread.quit()
            self.action_thread.wait(3000)
        super().closeEvent(event)
