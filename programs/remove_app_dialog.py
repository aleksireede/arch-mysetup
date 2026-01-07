from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QMessageBox
from PyQt5.QtCore import Qt


class RemoveAppDialog(QDialog):
    """Custom Wayland-safe remove application dialog."""

    def __init__(self, parent, apps):
        super().__init__(parent)
        self.setWindowTitle("Remove Applications")
        self.setWindowModality(Qt.ApplicationModal)
        self.selected_item = None

        layout = QVBoxLayout(self)

        # List widget
        self.list_widget = QListWidget(self)
        self.list_widget.addItems(apps)
        layout.addWidget(self.list_widget)

        # Remove button
        remove_btn = QPushButton("Remove Selected", self)
        remove_btn.clicked.connect(self.remove_selected)
        layout.addWidget(remove_btn)

        # Cancel button
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

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
            self.selected_item = item.text()
            self.accept()
