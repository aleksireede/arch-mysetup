import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QLabel
)

from gui.applist_editor_dialog import AppListEditorDialog

sys.path.append("programs")
from programs.apps_file import load_apps_from_file
from programs.installer_logic import is_app_installed, detect_install_method, app_install

class AppLoaderWorker(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def load_apps(self):
        try:
            apps = load_apps_from_file()
            self.finished.emit(apps)
        except Exception as e:
            self.error.emit(str(e))

class AppCheckWorker(QObject):
    finished = pyqtSignal(list)

    def __init__(self, apps):
        super().__init__()
        self.apps = apps

    def run(self):
        uninstalled_apps = [
            app for app in self.apps if not is_app_installed(app)
        ]
        self.finished.emit(uninstalled_apps)

class ArchAppInstaller(QMainWindow):
    def __init__(self, setup_window):
        super().__init__()
        self.worker = None
        self.refresh_button = None
        self.install_button = None
        self.select_all_button = None
        self.app_editor_btn = None
        self.back_button = None
        self.list_widget = None
        self.loading_label = None
        self.bottom_layout = None
        self.third_layout = None
        self.secondary_layout = None
        self.main_layout = None
        self.central_widget = None
        self.thread = None
        self.setup_window = setup_window
        self.setWindowTitle("Arch App Installer")
        self.setGeometry(100, 100, 500, 400)
        self.apps = []
        self.selected_apps = []
        self.init_ui()
        self.load_apps_async()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.secondary_layout = QHBoxLayout()
        self.third_layout = QHBoxLayout()
        self.bottom_layout = QHBoxLayout()

        # Loading label
        self.loading_label = QLabel("Loading apps...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # List widget to display Apps
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)

        # Add a back button
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back_to_setup)
        self.back_button.setFixedWidth(100)

        # Buttons
        self.app_editor_btn = QPushButton("App List Editor")
        self.app_editor_btn.clicked.connect(self.app_list_editor_dialog)

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.toggle_select_all_apps)

        self.install_button = QPushButton("Install Selected")
        self.install_button.clicked.connect(self.install_selected)
        self.install_button.setFixedWidth(200)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_apps_async)

        # Layouts
        self.secondary_layout.addWidget(self.back_button)
        self.secondary_layout.addStretch(1)
        self.secondary_layout.addWidget(self.app_editor_btn)
        self.secondary_layout.addStretch(2)

        self.third_layout.addWidget(self.select_all_button)
        self.third_layout.addStretch()
        self.third_layout.addWidget(self.refresh_button)

        self.bottom_layout.addWidget(self.install_button)

        # Add loading label and list widget
        self.main_layout.addLayout(self.secondary_layout)
        self.main_layout.addSpacing(20)
        self.main_layout.addWidget(self.loading_label)
        self.main_layout.addWidget(self.list_widget)
        self.main_layout.addSpacing(20)
        self.main_layout.addLayout(self.bottom_layout)

        self.central_widget.setLayout(self.main_layout)

    def load_apps_async(self):
        self.loading_label.show()
        self.list_widget.clear()

        self.thread = QThread()
        self.worker = AppLoaderWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.load_apps)
        self.worker.finished.connect(self.on_apps_loaded)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.error.connect(self.on_error)

        self.thread.start()

    def on_apps_loaded(self, apps):
        self.apps = apps
        self.refresh_app_list()
        self.loading_label.hide()

    def on_error(self, error_message):
        QMessageBox.critical(self, "Error", f"Failed to load apps: {error_message}")
        self.loading_label.hide()

    def refresh_app_list(self):
        self.list_widget.clear()
        loading_item = QListWidgetItem("Loading apps...")
        loading_item.setFlags(loading_item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsUserCheckable)
        self.list_widget.addItem(loading_item)

        # Stop the existing thread if it is running
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        # Create a new thread and worker for the refresh operation
        self.thread = QThread()
        self.worker = AppCheckWorker(self.apps)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_apps_checked)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def closeEvent(self, event):
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        event.accept()

    def on_apps_checked(self, uninstalled_apps):
        self.list_widget.clear()
        if not uninstalled_apps:
            item = QListWidgetItem("All apps installed!")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsUserCheckable)
            self.list_widget.addItem(item)
        else:
            for app in uninstalled_apps:
                item = QListWidgetItem(app)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                if app in self.selected_apps:
                    item.setCheckState(Qt.CheckState.Checked)
                else:
                    item.setCheckState(Qt.CheckState.Unchecked)
                self.list_widget.addItem(item)

    def toggle_select_all_apps(self):
        all_selected = all(
            self.list_widget.item(i).checkState() == Qt.CheckState.Checked
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).flags() & Qt.ItemFlag.ItemIsUserCheckable
        )
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(Qt.CheckState.Unchecked if all_selected else Qt.CheckState.Checked)

    def install_selected(self):
        selected_apps = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_apps.append(item.text())

        if selected_apps:
            confirm = QMessageBox.question(
                self, "Confirm Installation",
                f"Do you want to install the following apps?\n{', '.join(selected_apps)}",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                if len(selected_apps) > 1:
                    pacman_list = []
                    paru_list = []
                    for app in selected_apps:
                        method = detect_install_method(app)
                        if method == "paru":
                            paru_list.append(app)
                        elif method == "pacman":
                            pacman_list.append(app)
                    if pacman_list:
                        app_install(pacman_list, "pacman")
                    if paru_list:
                        app_install(paru_list, "paru")
                else:
                    for app in selected_apps:
                        method = detect_install_method(app)
                        app_install(app, method)
        else:
            QMessageBox.warning(self, "No Selection", "No apps selected for installation.")
        self.load_apps_async()

    def app_list_editor_dialog(self):
        dialog = AppListEditorDialog(self, self.apps)
        if dialog.exec():
            self.apps = dialog.get_apps()
            self.load_apps_async()

    def go_back_to_setup(self):
        self.setup_window.show()
        self.hide()
