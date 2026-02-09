import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem, \
    QMessageBox, QLabel, QFrame

parent_dir = str(Path(__file__).resolve().parent.parent.joinpath("programs"))
sys.path.append(parent_dir)

from installer_logic import (is_app_installed, list_all_installed_apps, remove_apps)


class AppUninstaller(QMainWindow):
    def __init__(self, setup_window):
        super().__init__()
        # Buttons
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
        self.apps = list_all_installed_apps()
        self.init_ui()

    def init_ui(self):
        self.main_window_frame = QWidget()
        self.setCentralWidget(self.main_window_frame)
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

        ## BEGIN Custom Back Button
        self.back_button_container = QFrame()
        self.back_button_container.setFixedSize(150, 45)

        self.frame_layout = QHBoxLayout(self.back_button_container)
        self.frame_layout.setContentsMargins(10, 0, 10, 0)
        self.frame_layout.setSpacing(5) # Small gap between arrow and text

        # Remove the large manual spacing and stretch if you want them centered
        self.frame_layout.setAlignment(Qt.AlignCenter) # Keeps group in the middle
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
        
        self.back_btn = QPushButton("←") # Using an icon or arrow
        self.back_lbl = QLabel("Back")
        
        # Layout
        self.frame_layout.addWidget(self.back_btn)
        self.frame_layout.addSpacing(20)
        self.frame_layout.addWidget(self.back_lbl)
        self.frame_layout.addStretch()
        
        # Button press
        self.back_button_container.mousePressEvent = lambda event: self.go_back_to_setup()
        self.back_btn.clicked.connect(self.go_back_to_setup)
        ## END Back Button

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.toggle_select_all_apps)

        self.install_button = QPushButton("Remove Selected")
        self.install_button.clicked.connect(self.remove_selected)
        self.install_button.setFixedWidth(200)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_app_list)

        # second layout
        self.secondary_layout.addWidget(self.back_button_container)
        self.secondary_layout.addStretch()

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

        self.main_window_frame.setLayout(self.main_layout)

    def refresh_app_list(self):
        """Refresh the list of Apps, only showing installed apps."""
        self.list_widget.clear()
        installed_apps = [
            app for app in self.apps if is_app_installed(app)]

        if installed_apps:
            for app in installed_apps:
                item = QListWidgetItem(app)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.list_widget.addItem(item)
        else:
            item = QListWidgetItem("No apps to remove.!")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable &
                          ~Qt.ItemFlag.ItemIsUserCheckable)
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
        self.refresh_app_list()

    def go_back_to_setup(self):
        self.previous_window.show()  # Show the setup window
        self.hide()  # Hide the current window
