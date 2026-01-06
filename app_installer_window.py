import subprocess
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QInputDialog, QDialog
from PyQt5.QtCore import Qt
import json
from remove_app_dialog import RemoveAppDialog
from installer_logic import (
    load_apps_from_json, is_app_installed, install_app, check_if_installed
)


class ArchAppInstaller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arch App Installer")
        self.setGeometry(100, 100, 500, 400)
        self.apps = load_apps_from_json()
        self.selected_apps=""
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        # List widget to display applications
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)

        # Add applications to the list
        self.refresh_app_list()

        # Buttons
        self.add_app_button = QPushButton("Add Applications to list")
        self.add_app_button.clicked.connect(self.add_applications)

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.toggle_select_all_apps)

        self.install_button = QPushButton("Install Selected")
        self.install_button.clicked.connect(self.install_selected)

        self.remove_app_button = QPushButton("Remove Applications from list")
        self.remove_app_button.clicked.connect(self.remove_applications)

        self.layout.addWidget(self.remove_app_button)

        # Add widgets to the layout
        self.layout.addWidget(self.add_app_button)
        self.layout.addWidget(self.select_all_button)
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.install_button)
        self.central_widget.setLayout(self.layout)

    def remove_applications(self):
        if not self.apps:
            QMessageBox.information(
                self, "Empty", "No applications to remove.")
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
        """Refresh the list of applications, hiding installed apps."""
        self.list_widget.clear()
        uninstalled_apps = [
            app for app in self.apps if not is_app_installed(app)]

        if not uninstalled_apps:
            item = QListWidgetItem("All apps installed!")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable &
                          ~Qt.ItemIsUserCheckable)
            self.list_widget.addItem(item)
        else:
            for app in uninstalled_apps:
                item = QListWidgetItem(app)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                if app in self.selected_apps:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
                self.list_widget.addItem(item)

    def add_applications(self):
        """Open a dialog to add new applications to the JSON file, checking availability first."""
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
                QMessageBox.information(self, "Available", msg)
            else:
                QMessageBox.warning(
                    self, "Not Found", f"{new_app} is not available in pacman or AUR.")

            self.apps.append(new_app)
            self.apps.sort()
            with open("apps.json", "w") as f:
                import json
                json.dump(self.apps, f)

            # 🔥 Reload apps from disk, then refresh UI
            self.apps = load_apps_from_json()
            self.refresh_app_list()

            QMessageBox.information(
                self, "Success", f"Added {new_app} to the list!")

    def toggle_select_all_apps(self):
        """Toggle between selecting and deselecting all apps."""
        all_selected = all(
            self.list_widget.item(i).checkState() == Qt.Checked
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).flags() & Qt.ItemIsUserCheckable
        )
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(
                    Qt.Unchecked if all_selected else Qt.Checked)

    def install_selected(self):
        selected_apps = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_apps.append(item.text())

        if selected_apps:
            confirm = QMessageBox.question(
                self, "Confirm Installation",
                f"Do you want to install the following apps?\n{', '.join(selected_apps)}",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirm == QMessageBox.Yes:
                for app in selected_apps:
                    if install_app(app):
                         QMessageBox.information(
                    self, "Success", "Installation process completed!")
                    else:
                        QMessageBox.warning(
                            self, "Warning", f"Failed to install {app}.")
                self.refresh_app_list()
        else:
            QMessageBox.warning(self, "No Selection",
                                "No apps selected for installation.")
