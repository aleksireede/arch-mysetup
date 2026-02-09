import subprocess
import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QMessageBox, QInputDialog, QHBoxLayout

parent_dir = str(Path(__file__).resolve().parent.parent.joinpath("programs"))
sys.path.append(parent_dir)

from apps_file import add_app_to_yaml, remove_app_from_yaml
from installer_logic import command_exists


class AppListEditorDialog(QDialog):
    def __init__(self, parent=None, apps=None):
        super().__init__(parent)
        self.setWindowTitle("App List Editor")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setGeometry(100,100,400,500)
        self.selected_item = None
        self.apps = apps

        # use vertical box layout
        layout = QHBoxLayout(self)
        button_layout = QVBoxLayout(self)
        list_layout = QVBoxLayout(self)

        # List widget
        self.list_widget = QListWidget(self)
        self.list_widget.addItems(apps)

        # Add button
        add_btn = QPushButton("Add app", self)
        add_btn.clicked.connect(self.add_apps)

        # OK button
        ok_btn = QPushButton("OK", self)
        ok_btn.clicked.connect(self.accept)

        # Remove button
        remove_btn = QPushButton("Remove Selected", self)
        remove_btn.clicked.connect(self.remove_selected)

        # Cancel button
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)

        # list
        list_layout.addWidget(self.list_widget)

        # button layout
        button_layout.addWidget(add_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()

        # main layout
        layout.addLayout(list_layout)
        layout.addLayout(button_layout)

    def remove_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.information(
                self, "No selection", "Please select an application to remove.")
            return
        confirm = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove '{item.text()}' from the application list?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            # remove from variable and the visible list then sort it
            self.apps.remove(item.text())
            current_row = self.list_widget.currentRow()
            if current_row >= 0:  # Check if an item is selected
                self.list_widget.takeItem(current_row)
            # :todo fix yaml remove
            remove_app_from_yaml(item.text())

            self.list_widget.sortItems()

    def add_apps(self):
        """Open a dialog to add new Apps to the main program, checking availability first."""
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

            if command_exists("paru"):
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
                # add item to variable and sort it and then add it to the visible list and sort that too
                self.apps.append(new_app)
                add_app_to_yaml(new_app)
                self.apps.sort()
                self.list_widget.addItem(new_app)
                self.list_widget.sortItems()
                QMessageBox.information(
                    self, "Success", msg + f"\nAdded {new_app} to the list!")
                # self.refresh_app_list()
            else:
                QMessageBox.warning(
                    self, "Not Found", f"{new_app} is not available in pacman or AUR.")

    def get_apps(self):
        return self.apps
