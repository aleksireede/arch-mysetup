import json
import subprocess
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem, \
    QMessageBox, QInputDialog, QDialog

from gui.remove_app_dialog import RemoveAppDialog

sys.path.append("programs")
from programs.installer_logic import (
    load_apps_from_json, is_app_installed, install_app, check_if_installed, detect_install_method, pacman_install,
    paru_install
)


class ArchAppInstaller(QMainWindow):
    def __init__(self, setup_window):
        super().__init__()
        self.remove_app_button = None
        self.install_button = None
        self.select_all_button = None
        self.add_app_button = None
        self.back_button = None
        self.refresh_button = None
        self.list_widget = None
        self.bottom_layout = None
        self.third_layout = None
        self.app_layout = None
        self.secondary_layout = None
        self.main_layout = None
        self.central_widget = None
        self.setup_window = setup_window  # Store the reference
        self.setWindowTitle("Arch App Installer")
        self.setGeometry(100, 100, 500, 400)
        self.apps = load_apps_from_json()
        self.selected_apps = []
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.secondary_layout = QHBoxLayout()
        self.app_layout = QHBoxLayout()
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
        self.add_app_button = QPushButton("Add Apps to list")
        self.add_app_button.clicked.connect(self.add_apps)

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.toggle_select_all_apps)

        self.install_button = QPushButton("Install Selected")
        self.install_button.clicked.connect(self.install_selected)
        self.install_button.setFixedWidth(200)

        self.remove_app_button = QPushButton("Remove Apps from list")
        self.remove_app_button.clicked.connect(self.remove_apps)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_app_list)

        # second layout
        self.secondary_layout.addWidget(self.back_button)
        self.secondary_layout.addStretch()

        # app layout
        self.app_layout.addWidget(self.remove_app_button)
        self.app_layout.addWidget(self.add_app_button)

        # select and refresh layout
        self.third_layout.addWidget(self.select_all_button)
        self.third_layout.addStretch()
        self.third_layout.addWidget(self.refresh_button)

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

        self.central_widget.setLayout(self.main_layout)

    def go_back_to_setup(self):
        self.setup_window.show()  # Show the setup window
        self.hide()  # Hide the current window

    def remove_apps(self):
        if not self.apps:
            QMessageBox.information(
                self, "Empty", "No Apps to remove.")
            return

        dialog = RemoveAppDialog(self, self.apps)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_item:
            item = dialog.selected_item

            # Remove from lists
            if item in self.apps:
                self.apps.remove(item)
            if item in self.selected_apps:
                self.selected_apps.remove(item)

            # Save changes
            self.apps.sort()
            with open("apps.json", "w") as f:
                json.dump(self.apps, f)

            # Refresh UI
            self.refresh_app_list()

            QMessageBox.information(
                self, "Removed", f"'{item}' removed successfully.")

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

    def add_apps(self):
        """Open a dialog to add new Apps to the JSON file, checking availability first."""
        new_app, ok = QInputDialog.getText(
            self, "Add Application", "Enter application name:"
        )
        if ok and new_app:
            if new_app in self.apps:
                QMessageBox.warning(
                    self, "Warning", f"{new_app} is already in the list.")
                return

            available_in = []
            try:
                subprocess.run(
                    ["pacman", "-Si", new_app],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
                )
                available_in.append("pacman")
            except subprocess.CalledProcessError:
                pass

            if check_if_installed("paru"):
                try:
                    subprocess.run(
                        ["paru", "-Si", new_app],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
                    )
                    available_in.append("AUR")
                except subprocess.CalledProcessError:
                    pass

            if available_in:
                msg = f"{new_app} is available in: {', '.join(available_in)}"
                # QMessageBox.information(self, "Available", msg)
                self.apps.append(new_app)
                self.apps.sort()
                with open("apps.json", "w") as f:
                    import json
                    json.dump(self.apps, f)
                QMessageBox.information(
                    self, "Success", msg + f"\nAdded {new_app} to the list!")
                # 🔥 Reload apps from disk, then refresh UI
                self.apps = load_apps_from_json()
                self.refresh_app_list()
            else:
                QMessageBox.warning(
                    self, "Not Found", f"{new_app} is not available in pacman or AUR.")

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
                        pacman_install(pacman_list)
                    if paru_list:
                        paru_install(paru_list)
                else:
                    for app in selected_apps:
                        install_app(app)
        else:
            QMessageBox.warning(self, "No Selection",
                                "No apps selected for installation.")
        self.refresh_app_list()

    def go_back_to_setup(self):
        self.setup_window.show()  # Show the setup window
        self.hide()  # Hide the current window
