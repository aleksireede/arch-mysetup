import sys
from pathlib import Path

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QLabel
)
from apps_file import load_apps_from_file
from installer_logic import (
    is_app_installed, detect_install_method, app_install
)

from applist_editor_dialog import AppListEditorDialog

parent_dir = str(Path(__file__).resolve().parent.parent.joinpath("programs"))
sys.path.append(parent_dir)


class AppManagerWorker(QObject):
    finished = pyqtSignal(list, list) # Returns (all_apps, uninstalled_apps)
    error = pyqtSignal(str)

    def run(self):
        try:
            # 1. Get the full list from the file
            all_apps = load_apps_from_file()
            # 2. Filter for what's actually missing
            uninstalled = [app for app in all_apps if not is_app_installed(app)]
            # 3. Return both so the UI knows the full list AND the display list
            self.finished.emit(all_apps, uninstalled)
        except Exception as e:
            self.error.emit(str(e))


class ArchAppInstaller(QMainWindow):
    def __init__(self, setup_window):
        super().__init__()
        self.thread = None
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

        # Add Apps to the list
        self.refresh_app_list()

        # BEGIN Custom Back Button
        self.back_button_container = QFrame()
        self.back_button_container.setFixedSize(150, 45)

        self.frame_layout = QHBoxLayout(self.back_button_container)
        self.frame_layout.setContentsMargins(10, 0, 10, 0)
        self.frame_layout.setSpacing(5)  # Small gap between arrow and text

        # Remove the large manual spacing and stretch if you want them centered
        self.frame_layout.setAlignment(
            Qt.AlignCenter)  # Keeps group in the middle
        self.back_button_container.setStyleSheet("""
            QFrame {
                background-color: #991212;
                border-radius: 5px;
            }
            QFrame:hover {
                background-color: #ba1616; /* Lighter red on hover */
            }
            QLabel, QPushButton {
                background-color: transparent; /* Makes children take Frame's color */
                color: white;
                font-weight: bold;
                border: none;
            }
            """)

        self.back_btn = QPushButton("←")  # Using an icon or arrow
        self.back_lbl = QLabel("Back")

        # Layout
        self.frame_layout.addWidget(self.back_btn)
        self.frame_layout.addSpacing(20)
        self.frame_layout.addWidget(self.back_lbl)
        self.frame_layout.addStretch()

        # Button press
        self.back_button_container.mousePressEvent = lambda event: self.go_back_to_setup()
        self.back_btn.clicked.connect(self.go_back_to_setup)
        # END Back Button

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

        # second layout
        self.secondary_layout.addWidget(self.back_button_container)
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
        if self.thread and self.thread.isRunning():
            return

        self.loading_label.show()
        self.loading_label.setText("Syncing app list...")

        self.thread = QThread()
        self.worker = AppManagerWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        # Connect to the final UI updater
        self.worker.finished.connect(self.update_ui_with_apps)
        self.worker.error.connect(self.on_error)

        # Standard Cleanup
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.cleanup_thread)

        self.thread.start()

    def cleanup_thread(self):
        self.thread = None
        self.worker = None

    def on_apps_loaded(self, apps):
        self.apps = apps

        # SAFETY: Ensure the 'loading' thread is fully dead before starting 'check' thread
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        self.loading_label.setText("Checking installation status...")

        self.thread = QThread()
        self.worker = AppManagerWorker(self.apps)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        # Don't forget this connection!
        self.worker.finished.connect(self.on_apps_checked)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.cleanup_thread)

        self.thread.start()

    def on_error(self, error_message):
        QMessageBox.critical(
            self, "Error", f"Failed to load apps: {error_message}")
        self.loading_label.hide()

    def refresh_app_list(self):
        """Only handles UI state before/during the check"""
        self.list_widget.clear()
        loading_item = QListWidgetItem("Checking system for installed apps...")
        loading_item.setFlags(loading_item.flags() & ~
        Qt.ItemFlag.ItemIsSelectable)
        self.list_widget.addItem(loading_item)
        # Don't start a thread here; let load_apps_async handle it.

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            # 1. Ask the thread to stop
            self.thread.quit()
            # 2. Block the UI for a moment to let it finish safely
            if not self.thread.wait(3000):  # Wait up to 3 seconds
                print("Thread timed out, terminating...")
                self.thread.terminate()
        event.accept()

    def on_apps_checked(self, uninstalled_apps):
        # Hide loading UI
        self.loading_label.hide()

        self.list_widget.clear()
        if not uninstalled_apps:
            item = QListWidgetItem("All apps installed!")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.list_widget.addItem(item)
        else:
            for app in uninstalled_apps:
                item = QListWidgetItem(app)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(
                    Qt.CheckState.Checked if app in self.selected_apps else Qt.CheckState.Unchecked)
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
                item.setCheckState(
                    Qt.CheckState.Unchecked if all_selected else Qt.CheckState.Checked)

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
            QMessageBox.warning(self, "No Selection",
                                "No apps selected for installation.")
        self.load_apps_async()

    def update_ui_with_apps(self, all_apps, uninstalled_apps):
        """The single point of entry for your UI data"""
        self.apps = all_apps  # Keep the master list for the editor
        self.loading_label.hide()
        self.list_widget.clear()

        if not uninstalled_apps:
            item = QListWidgetItem("All apps are currently installed!")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.list_widget.addItem(item)
        else:
            for app in uninstalled_apps:
                item = QListWidgetItem(app)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                # Check if it was previously selected
                state = Qt.Checked if app in self.selected_apps else Qt.Unchecked
                item.setCheckState(state)
                self.list_widget.addItem(item)

    def app_list_editor_dialog(self):
        dialog = AppListEditorDialog(self, self.apps)
        if dialog.exec():
            self.apps = dialog.get_apps()
            self.load_apps_async()

    def go_back_to_setup(self):
        self.setup_window.show()
        self.hide()
