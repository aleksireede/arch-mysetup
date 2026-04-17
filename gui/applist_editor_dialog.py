import subprocess
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QMessageBox, QInputDialog, QHBoxLayout, \
    QListWidgetItem

from programs.apps_file import add_app_to_yaml, get_app_source, remove_app_from_yaml
from programs.installer_logic import (
    command_exists,
    detect_installed_method,
    get_install_method_from_source,
    is_app_installed,
    remove_apps,
)
try:
    from .theme import configure_dialog
except ImportError:
    from theme import configure_dialog


class AppListEditorDialog(QDialog):
    def __init__(self, parent=None, apps=None):
        super().__init__(parent)
        self.setWindowTitle("App List Editor")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        configure_dialog(self, width=620, height=720, min_width=560, min_height=640)
        self.selected_item = None
        self.apps = apps
        self.search_icon_path = Path(__file__).resolve().parent.parent.joinpath("icons", "search.svg")

        # use vertical box layout
        layout = QHBoxLayout(self)
        button_layout = QVBoxLayout()
        list_layout = QVBoxLayout()

        # List widget
        self.list_widget = QListWidget(self)
        self.populate_list()

        # Add button
        add_btn = QPushButton("Add app", self)
        add_btn.clicked.connect(self.add_apps)

        # OK button
        ok_btn = QPushButton("Apply", self)
        ok_btn.clicked.connect(self.accept)

        # Remove button
        remove_btn = QPushButton("Remove Selected", self)
        remove_btn.clicked.connect(self.remove_selected)

        # Search button
        search_btn = QPushButton("Search", self)
        search_btn.setIcon(QIcon(str(self.search_icon_path)))
        search_btn.clicked.connect(self.search_app)

        # Cancel button
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)

        # list
        list_layout.addWidget(self.list_widget)

        # button layout
        button_layout.addStretch()
        button_layout.addWidget(add_btn)
        button_layout.addWidget(search_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addSpacing(15)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        # main layout
        layout.addLayout(list_layout)
        layout.addLayout(button_layout)

    def populate_list(self):
        self.list_widget.clear()
        for app in sorted(self.apps):
            item = QListWidgetItem(app)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)

    def get_checked_apps(self):
        checked_apps = []
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                checked_apps.append(item.text())
        return checked_apps

    def remove_selected(self):
        selected_apps = self.get_checked_apps()
        if not selected_apps:
            QMessageBox.information(
                self, "No selection", "Please check at least one application to remove.")
            return
        confirm = QMessageBox.question(
            self,
            "Confirm Removal",
            "Remove the selected applications from the application list and try to uninstall them from the system?\n"
            f"{', '.join(selected_apps)}",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            removal_groups = {"pacman": [], "paru": []}
            not_installed = []
            unknown_source = []

            for app_name in selected_apps:
                source = get_app_source(app_name)
                remove_method = get_install_method_from_source(source)
                if remove_method is None:
                    remove_method = detect_installed_method(app_name)

                if app_name in self.apps:
                    self.apps.remove(app_name)
                remove_app_from_yaml(app_name)

                if not is_app_installed(app_name):
                    not_installed.append(app_name)
                    continue

                if remove_method is None:
                    unknown_source.append(app_name)
                    continue

                removal_groups[remove_method].append(app_name)

            self.populate_list()

            started_uninstalls = []
            failed_uninstalls = []
            for method, apps in removal_groups.items():
                if not apps:
                    continue
                process = remove_apps(apps, method)
                if process:
                    started_uninstalls.extend(f"{app} ({method})" for app in apps)
                else:
                    failed_uninstalls.extend(apps)

            messages = [f"Removed from list: {', '.join(selected_apps)}"]
            if started_uninstalls:
                messages.append(f"Uninstall started: {', '.join(started_uninstalls)}")
            if not_installed:
                messages.append(f"Not installed: {', '.join(not_installed)}")
            if unknown_source:
                messages.append(f"Could not determine uninstall source: {', '.join(unknown_source)}")
            if failed_uninstalls:
                messages.append(f"Could not start uninstall command: {', '.join(failed_uninstalls)}")

            if failed_uninstalls or unknown_source:
                QMessageBox.warning(self, "Removal Summary", "\n".join(messages))
            else:
                QMessageBox.information(self, "Removal Summary", "\n".join(messages))

    def add_apps(self):
        """Open a dialog to add one or more apps, checking availability first."""
        new_apps_text, ok = QInputDialog.getText(
            self, "Add Application", "Enter application names separated by commas:"
        )
        if not ok:
            return

        requested_apps = []
        seen = set()
        for raw_name in new_apps_text.split(","):
            app_name = raw_name.strip()
            if not app_name:
                continue
            normalized = app_name.casefold()
            if normalized in seen:
                continue
            seen.add(normalized)
            requested_apps.append(app_name)

        if not requested_apps:
            QMessageBox.information(self, "Add Application", "Please enter at least one application name.")
            return

        added_apps = []
        duplicate_apps = []
        not_found_apps = []

        for new_app in requested_apps:
            if new_app in self.apps:
                duplicate_apps.append(new_app)
                continue

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
                self.apps.append(new_app)
                add_app_to_yaml(new_app)
                added_apps.append(f"{new_app} ({', '.join(available_in)})")
            else:
                not_found_apps.append(new_app)

        self.apps.sort()
        self.populate_list()

        messages = []
        if added_apps:
            messages.append(f"Added: {', '.join(added_apps)}")
        if duplicate_apps:
            messages.append(f"Already in list: {', '.join(duplicate_apps)}")
        if not_found_apps:
            messages.append(f"Not found in pacman or AUR: {', '.join(not_found_apps)}")

        if not added_apps:
            QMessageBox.warning(self, "Add Application", "\n".join(messages))
        else:
            QMessageBox.information(self, "Add Application", "\n".join(messages))

    def get_apps(self):
        return self.apps

    def search_app(self):
        search_text, ok = QInputDialog.getText(
            self, "Search Application", "Enter app name to search:"
        )
        if not ok:
            return

        query = search_text.strip()
        if not query:
            QMessageBox.information(self, "Search", "Please enter an application name.")
            return

        lower_query = query.lower()
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if lower_query in item.text().lower():
                self.list_widget.setCurrentRow(index)
                self.list_widget.scrollToItem(item)
                return

        QMessageBox.information(self, "Not Found", f"No application found for '{query}'.")
