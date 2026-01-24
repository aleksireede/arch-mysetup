import sys
from pathlib import Path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout, QMessageBox, \
    QInputDialog, QLineEdit, QSizePolicy

sys.path.append("programs")
from programs.installer_logic import install_paru, add_samba_drive, command_exists


class SetupWindow(QMainWindow):
    open_installer = pyqtSignal()  # Signal to open the installer
    open_uninstaller = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Buttons
        self.install_button = None
        self.remove_button = None
        self.add_network_drive_button = None
        self.install_paru_button = None
        # end buttons
        self.paru_status = None
        self.paru_label = None
        # layout horizontal or vertical
        self.paru_layout = None
        self.layout = None
        # todo: explain widget
        self.central_widget = None
        # Set the window title text
        self.setWindowTitle("Setup: Install Paru")
        # set window size
        self.setGeometry(100, 100, 400, 300)
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)  # Set layout directly on central widget

        # Paru section
        self.paru_layout = QHBoxLayout()
        self.paru_label = QLabel("Paru (AUR Helper):")
        self.paru_status = QLabel()
        self.install_paru_button = QPushButton("Install Paru")
        self.update_paru_status()
        self.install_paru_button.clicked.connect(self.handle_install_paru)

        # Add stretch to push buttons to the left and right
        self.paru_layout.addWidget(self.paru_label)
        self.paru_layout.addWidget(self.paru_status)
        self.paru_layout.addWidget(self.install_paru_button)
        self.paru_layout.addStretch()  # Pushes widgets to the left

        # Add Network Drive button
        self.add_network_drive_button = QPushButton("Add Network Drive (Samba)")
        self.add_network_drive_button.clicked.connect(self.add_network_drive)

        # Install apps button
        self.install_button = QPushButton("Install apps")
        self.install_button.clicked.connect(self.open_installer.emit)

        # Uninstall apps button
        self.remove_button = QPushButton("Uninstall")
        self.remove_button.clicked.connect(self.open_uninstaller.emit)

        # Set size policies for buttons
        self.install_paru_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.add_network_drive_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.install_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Add to main layout with stretch
        self.layout.addLayout(self.paru_layout)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.install_button)
        self.layout.addWidget(self.remove_button)
        self.layout.addWidget(self.add_network_drive_button)
        self.layout.addSpacing(20)

        # Allow window to resize
        self.setMinimumSize(400, 200)

    def update_paru_status(self):
        checkmark_path = Path(Path(__file__).parent.parent.resolve()).joinpath("icons/checkmark.svg")
        red_x_path = Path(Path(__file__).parent.parent.resolve()).joinpath("icons/red_x.svg")
        """Update the Paru status icon or text."""
        if command_exists("paru"):
            self.paru_status.setPixmap(QPixmap(str(checkmark_path)).scaled(20, 20))
            self.install_paru_button.setText("Installed")
        else:
            self.paru_status.setPixmap(QPixmap(str(red_x_path)).scaled(20, 20))

    def handle_install_paru(self):
        print(install_paru())
        if command_exists("paru"):
            QMessageBox.information(self, "Installed", "Paru is already installed!")
        else:
            if install_paru():
                QMessageBox.information(self, "Success", "Paru installed successfully!")
                self.update_paru_status()
            else:
                QMessageBox.critical(self, "Error", "Failed to install Paru.")

    def add_network_drive(self):
        """Prompt for Samba share details and add to fstab."""
        share_path, ok1 = QInputDialog.getText(
            self, "Add Network Drive", "Enter Samba share path (e.g., 192.168.1.177/backup):"
        )
        if not ok1:
            return

        mount_point, ok2 = QInputDialog.getText(
            self, "Add Network Drive", "Enter mount point (e.g., /media/server):"
        )
        if not ok2:
            return

        username, ok3 = QInputDialog.getText(
            self, "Add Network Drive", "Enter Samba username:"
        )
        if not ok3:
            return

        password, ok4 = QInputDialog.getText(
            self, "Add Network Drive", "Enter Samba password:", QLineEdit.Password
        )
        if not ok4:
            return

        try:
            if add_samba_drive(share_path, mount_point, username, password):
                QMessageBox.information(self, "Success", "Network drive added successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to add network drive.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add network drive: {e}")

    def open_app_installer(self):
        self.app_installer_callback()
        self.close()
