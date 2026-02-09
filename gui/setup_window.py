import shutil
import sys
from pathlib import Path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout, QMessageBox, \
    QInputDialog, QLineEdit, QSizePolicy

programs_dir = str(Path(__file__).resolve().parent.parent.joinpath("programs"))
sys.path.append(programs_dir)

scripts_dir = str(Path(__file__).resolve().parent.parent.joinpath("scripts"))
sys.path.append(scripts_dir)

from detect_gpu import detect_gpu_vendor, install_drivers
from installer_logic import install_paru, add_samba_drive, command_exists


def gpu_driver_install():
    vendor = detect_gpu_vendor()
    install_drivers(vendor)


class SetupWindow(QMainWindow):
    open_installer = pyqtSignal()  # Signal to open the installer
    open_uninstaller = pyqtSignal()
    open_tweaks = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Buttons
        self.outer_bottom_layout = None
        self.bottom_layout = None
        self.gpudrv_label = None
        self.gpudrv_status = None
        self.gpudrv_button = None
        self.gpudrv_layout = None
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
        # main window
        self.main_window = None
        # Set the window title text
        self.setWindowTitle("Setup: Install Paru")
        # set window size
        self.setGeometry(100, 100, 400, 300)
        self.init_ui()

    def init_ui(self):
        self.main_window = QWidget()
        self.setCentralWidget(self.main_window)
        self.layout = QVBoxLayout(self.main_window)  # Set layout directly on central widget

        # GPU Driver Section
        self.gpudrv_layout = QHBoxLayout()
        self.gpudrv_button = QPushButton("Install GPU Drivers")
        self.gpudrv_label = QLabel("GPU Drivers:")
        self.gpudrv_button.clicked.connect(gpu_driver_install)
        self.gpudrv_status = QLabel()
        self.update_gpu_status()

        # Gpu driver layout setup
        self.gpudrv_layout.addWidget(self.gpudrv_label)
        self.gpudrv_layout.addWidget(self.gpudrv_status)
        self.gpudrv_layout.addWidget(self.gpudrv_button)
        self.gpudrv_layout.addStretch()

        # Paru section
        self.paru_layout = QHBoxLayout()
        self.paru_label = QLabel("Paru (AUR Helper):")
        self.paru_status = QLabel()
        self.install_paru_button = QPushButton("Install Paru")
        self.update_paru_status()
        self.install_paru_button.clicked.connect(self.handle_install_paru)

        # add paru widgets to paru layout
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
        
        self.tweak_btn = QPushButton("Tweaks")
        self.tweak_btn.clicked.connect(self.open_tweaks.emit)

        # Set size policies for buttons
        self.install_paru_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.gpudrv_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.add_network_drive_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.install_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.remove_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Bottom Button layout
        self.bottom_layout = QVBoxLayout()
        #self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.install_button)
        self.bottom_layout.addWidget(self.remove_button)
        self.bottom_layout.addWidget(self.add_network_drive_button)
        #self.bottom_layout.addStretch()

        # Bottom outer layout
        self.outer_bottom_layout = QHBoxLayout()
        self.outer_bottom_layout.addStretch()
        self.outer_bottom_layout.addLayout(self.bottom_layout)
        self.outer_bottom_layout.addStretch()

        # Add to main layout with stretch
        self.layout.addSpacing(20)
        self.layout.addLayout(self.paru_layout)
        self.layout.addLayout(self.gpudrv_layout)
        self.layout.addSpacing(20)
        self.layout.addLayout(self.outer_bottom_layout)
        self.layout.addSpacing(20)
        self.layout.addStretch()

        # Allow window to resize
        self.setMinimumSize(400, 200)

    def update_gpu_status(self):
        checkmark_path = Path(Path(__file__).parent.parent.resolve()).joinpath("icons/checkmark.svg")
        red_x_path = Path(Path(__file__).parent.parent.resolve()).joinpath("icons/red_x.svg")
        vendor = detect_gpu_vendor()
        # :todo fix amd detection
        if vendor == "AMD" and shutil.which("mesa"):
            self.gpudrv_status.setPixmap(QPixmap(str(checkmark_path)).scaled(20, 20))
        elif vendor == "Intel" and shutil.which("intel-virtual-output"):
            self.gpudrv_status.setPixmap(QPixmap(str(checkmark_path)).scaled(20, 20))
        elif vendor == "NVIDIA" and shutil.which("nvidia-modprobe"):
            self.gpudrv_status.setPixmap(QPixmap(str(checkmark_path)).scaled(20, 20))
        else:
            self.gpudrv_status.setPixmap(QPixmap(str(red_x_path)).scaled(20, 20))

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
