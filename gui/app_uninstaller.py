import sys
from pathlib import Path

from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem, \
    QMessageBox

parent_dir = str(Path(__file__).resolve().parent.parent.joinpath("programs"))
sys.path.append(parent_dir)

from programs.installer_logic import (list_all_installed_apps, remove_apps)

try:
    from .ui_helpers import create_back_button, create_select_refresh_row
    from .theme import apply_dark_theme
except ImportError:
    from ui_helpers import create_back_button, create_select_refresh_row
    from theme import apply_dark_theme


class AppListWorker(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def run(self):
        try:
            self.finished.emit(list_all_installed_apps())
        except Exception as e:
            self.error.emit(str(e))


class AppUninstaller(QMainWindow):
    def __init__(self, setup_window):
        super().__init__()
        self.thread = None
        self.worker = None
        # Buttons
        self.back_lbl = None
        self.back_btn = None
        self.frame_layout = None
        self.back_button_container = None
        self.install_button = None
        self.select_all_button = None
        self.back_button = None
        self.refresh_button = None
        # layouts
        self.list_widget = None
        self.bottom_layout = None
        self.third_layout = None
        self.app_layout = None
        self.secondary_layout = None
        self.main_layout = None
        self.main_window_frame = None
        # Main window for back button reference
        self.previous_window = setup_window  # Store the reference
        # Window title text
        self.setWindowTitle("Arch App Uninstaller")
        self.setGeometry(100, 100, 500, 400)
        # app list
        self.apps = []
        self.init_ui()

    def init_ui(self):
        self.main_window_frame = QWidget()
        self.setCentralWidget(self.main_window_frame)
        apply_dark_theme(self)
        self.main_layout = QVBoxLayout()
        self.secondary_layout = QHBoxLayout()
        self.app_layout = QHBoxLayout()
        self.third_layout = QHBoxLayout()
        self.bottom_layout = QHBoxLayout()

        # List widget to display Apps
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)

        # Add Apps to the list
        self.refresh_app_list_async()

        self.back_button_container, self.back_btn, self.back_lbl, self.frame_layout = create_back_button(
            self.go_back_to_setup
        )

        self.install_button = QPushButton("Remove Selected")
        self.install_button.clicked.connect(self.remove_selected)
        self.install_button.setFixedWidth(200)

        # second layout
        self.secondary_layout.addWidget(self.back_button_container)
        self.secondary_layout.addStretch()

        # select and refresh layout
        self.third_layout, self.select_all_button, self.refresh_button = create_select_refresh_row(
            self.toggle_select_all_apps, self.refresh_app_list_async
        )

        # bottom layout
        self.bottom_layout.addWidget(self.install_button)

        # add the layouts to the main one
        self.main_layout.addLayout(self.secondary_layout)
        self.main_layout.addSpacing(20)
        self.main_layout.addLayout(self.app_layout)
        self.main_layout.addLayout(self.third_layout)
        self.main_layout.addWidget(self.list_widget)
        self.main_layout.addSpacing(20)
        self.main_layout.addLayout(self.bottom_layout)

        self.main_window_frame.setLayout(self.main_layout)

    def refresh_app_list(self):
        """Render current installed apps in the list widget."""
        self.list_widget.clear()
        if self.apps:
            for app in self.apps:
                item = QListWidgetItem(app)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.list_widget.addItem(item)
        else:
            item = QListWidgetItem("No apps to remove.!")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable &
                          ~Qt.ItemFlag.ItemIsUserCheckable)
            self.list_widget.addItem(item)

    def refresh_app_list_async(self):
        if self.thread and self.thread.isRunning():
            return

        self.list_widget.clear()
        loading_item = QListWidgetItem("Refreshing installed app list...")
        loading_item.setFlags(loading_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.list_widget.addItem(loading_item)

        self.thread = QThread()
        self.worker = AppListWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.on_apps_loaded)
        self.worker.error.connect(self.on_refresh_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.cleanup_thread)

        self.thread.start()

    def on_apps_loaded(self, apps):
        self.apps = apps
        self.refresh_app_list()

    def on_refresh_error(self, error_message):
        QMessageBox.critical(self, "Error", f"Failed to refresh app list: {error_message}")
        self.apps = []
        self.refresh_app_list()

    def cleanup_thread(self):
        self.thread = None
        self.worker = None

    def toggle_select_all_apps(self):
        """Toggle between selecting and deselecting all apps."""
        all_selected = all(
            self.list_widget.item(i).checkState() == Qt.CheckState.Checked
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).flags() & Qt.ItemFlag.ItemIsUserCheckable
        )
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(
                    Qt.CheckState.Unchecked if all_selected else Qt.CheckState.Checked)

    def remove_selected(self):
        selected_apps = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_apps.append(item.text())

        if selected_apps:
            confirm = QMessageBox.question(
                self, "Confirm Remove",
                f"Do you want to remove the following apps?\n{', '.join(selected_apps)}",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                remove_apps(selected_apps, "paru")
        else:
            QMessageBox.warning(self, "No Selection",
                                "No apps selected for installation.")
        self.refresh_app_list_async()

    def go_back_to_setup(self):
        self.previous_window.show()  # Show the setup window
        self.hide()  # Hide the current window

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(3000)
        event.accept()
