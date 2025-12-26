from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QHBoxLayout, QMessageBox, QInputDialog, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from installer_logic import install_paru, install_flatpak, check_if_installed, add_samba_drive

class SetupWindow(QMainWindow):
    def __init__(self, app_installer_callback):
        super().__init__()
        self.setWindowTitle("Setup: Install Paru & Flatpak")
        self.setGeometry(100, 100, 400, 300)
        self.app_installer_callback = app_installer_callback
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        # Paru
        self.paru_layout = QHBoxLayout()
        self.paru_label = QLabel("Paru (AUR Helper):")
        self.paru_status = QLabel()
        self.update_paru_status()
        self.install_paru_button = QPushButton("Install Paru")
        self.install_paru_button.clicked.connect(self.handle_install_paru)
        self.paru_layout.addWidget(self.paru_label)
        self.paru_layout.addWidget(self.paru_status)
        self.paru_layout.addWidget(self.install_paru_button)

        # Flatpak
        self.flatpak_layout = QHBoxLayout()
        self.flatpak_label = QLabel("Flatpak:")
        self.flatpak_status = QLabel()
        self.update_flatpak_status()
        self.install_flatpak_button = QPushButton("Install Flatpak")
        self.install_flatpak_button.clicked.connect(self.handle_install_flatpak)
        self.flatpak_layout.addWidget(self.flatpak_label)
        self.flatpak_layout.addWidget(self.flatpak_status)
        self.flatpak_layout.addWidget(self.install_flatpak_button)

        # Add Network Drive
        self.add_network_drive_button = QPushButton("Add Network Drive (Samba)")
        self.add_network_drive_button.clicked.connect(self.add_network_drive)

        # Proceed button
        self.proceed_button = QPushButton("Proceed to App Installation")
        self.proceed_button.clicked.connect(self.open_app_installer)

        # Add to main layout
        self.layout.addLayout(self.paru_layout)
        self.layout.addLayout(self.flatpak_layout)
        self.layout.addWidget(self.add_network_drive_button)
        self.layout.addWidget(self.proceed_button)
        self.central_widget.setLayout(self.layout)

    def update_paru_status(self):
        """Update the Paru status icon or text."""
        if check_if_installed("paru"):
            try:
                self.paru_status.setPixmap(QPixmap("checkmark.svg").scaled(20, 20))
            except:
                self.paru_status.setText("✓")
        else:
            try:
                self.paru_status.setPixmap(QPixmap("red_x.svg").scaled(20, 20))
            except:
                self.paru_status.setText("✗")

    def update_flatpak_status(self):
        """Update the Flatpak status icon or text."""
        if check_if_installed("flatpak"):
            try:
                self.flatpak_status.setPixmap(QPixmap("checkmark.svg").scaled(20, 20))
            except:
                self.flatpak_status.setText("✓")
        else:
            try:
                self.flatpak_status.setPixmap(QPixmap("red_x.svg").scaled(20, 20))
            except:
                self.flatpak_status.setText("✗")

    def handle_install_paru(self):
        if install_paru():
            QMessageBox.information(self, "Success", "Paru installed successfully!")
            self.update_paru_status()
        else:
            QMessageBox.critical(self, "Error", "Failed to install Paru.")

    def handle_install_flatpak(self):
        if install_flatpak():
            QMessageBox.information(self, "Success", "Flatpak installed successfully!")
            self.update_flatpak_status()
        else:
            QMessageBox.critical(self, "Error", "Failed to install Flatpak.")

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
