import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem, \
    QMessageBox

from gui.applist_editor_dialog import AppListEditorDialog

sys.path.append("programs")
from programs.apps_file import load_apps_from_file
from programs.installer_logic import (
    is_app_installed, detect_install_method, app_install
)


class ArchAppInstaller(QMainWindow):
    def __init__(self, setup_window):
        super().__init__()
        self.app_editor_btn = None
        self.install_button = None
        self.select_all_button = None
        self.back_button = None
        self.refresh_button = None
        self.list_widget = None
        self.bottom_layout = None
        self.third_layout = None
        self.secondary_layout = None
        self.main_layout = None
        self.central_widget = None
        self.setup_window = setup_window  # Store the reference
        self.setWindowTitle("Arch App Installer")
        self.setGeometry(100, 100, 500, 400)
        self.apps = load_apps_from_file()
        self.selected_apps = []
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.secondary_layout = QHBoxLayout()
        self.third_layout = QHBoxLayout()
        self.bottom_layout = QHBoxLayout()

        # List widget to display Apps
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)

        # Add Apps to the list
        self.refresh_app_list()

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
        self.refresh_button.clicked.connect(self.refresh_app_list)

        # second layout
        self.secondary_layout.addWidget(self.back_button)
        self.secondary_layout.addStretch(1)
        self.secondary_layout.addWidget(self.app_editor_btn)
        self.secondary_layout.addStretch(2)

        # select and refresh layout
        self.third_layout.addWidget(self.select_all_button)
        self.third_layout.addStretch()
        self.third_layout.addWidget(self.refresh_button)

        # bottom layout
        self.bottom_layout.addWidget(self.install_button)

        # add the layouts to the main one
        self.main_layout.addLayout(self.secondary_layout)
        self.main_layout.addSpacing(20)
        self.main_layout.addLayout(self.third_layout)
        self.main_layout.addWidget(self.list_widget)
        self.main_layout.addSpacing(20)
        self.main_layout.addLayout(self.bottom_layout)

        self.central_widget.setLayout(self.main_layout)

    def app_list_editor_dialog(self):
        dialog = AppListEditorDialog(self, self.apps)
        if dialog.exec():  # or exec_() depending on Qt version
            self.apps = dialog.get_apps()
            self.refresh_app_list()

    def refresh_app_list(self):
        """Refresh the list of Apps, hiding installed apps."""
        self.list_widget.clear()
        uninstalled_apps = [
            app for app in self.apps if not is_app_installed(app)]

        if not uninstalled_apps:
            item = QListWidgetItem("All apps installed!")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable &
                          ~Qt.ItemFlag.ItemIsUserCheckable)
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
            # separate packages into aur and pacman list
            if confirm == QMessageBox.Yes:
                if len(selected_apps) > 1:
                    pacman_list = []
                    paru_list = []
                    # add apps to pacman and paru list respectively
                    for app in selected_apps:
                        method = detect_install_method(app)
                        if method == "paru":
                            paru_list.append(app)
                        elif method == "pacman":
                            pacman_list.append(app)
                    # check that the lists are not empty
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
        self.refresh_app_list()

    def go_back_to_setup(self):
        self.setup_window.show()  # Show the setup window
        self.hide()  # Hide the current window
