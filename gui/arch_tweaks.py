import sys
import subprocess
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget,
                             QPushButton, QListWidget, QListWidgetItem, QMessageBox, QHBoxLayout, QLabel, QFrame)


class ArchTweaks(QMainWindow):
    def __init__(self, setup_window=None):
        super().__init__()
        self.setup_window = setup_window
        self.setWindowTitle("Arch Linux Custom Tweaks")
        self.setGeometry(100, 100, 500, 500)

        # Define tweaks: { Display Name : Bash Command }
        self.tweaks = {
            "Enable Multilib Repository": "pkexec sed -i '/^#\[multilib\]/,/^#Include = \/etc\/pacman.d\/mirrorlist/ s/^#//' /etc/pacman.conf && pkexec pacman -Sy",
            "Enable Parallel Downloads (Pacman)": "pkexec sed -i 's/^#ParallelDownloads/ParallelDownloads/' /etc/pacman.conf",
            "Optimize Mirrorlist (Reflector)": "pkexec reflector --latest 20 --protocol https --sort rate --save /etc/pacman.d/mirrorlist",
            "Enable Color in Pacman": "pkexec sed -i 's/^#Color/Color/' /etc/pacman.conf",
            "Enable CPU Performance Mode": "pkexec pacman -S --needed cpupower --noconfirm && echo \"governor='performance'\" | pkexec tee /etc/default/cpupower && pkexec systemctl enable --now cpupower",
            "Install Yay (AUR Helper)": "pacman -Qi yay || pkexec pacman -S --needed git base-devel && git clone https://aur.archlinux.org/yay.git && cd yay && makepkg -si --noconfirm",
            "Install Paru (Rust AUR Helper)": "pacman -Qi paru || (pkexec pacman -S --needed base-devel git && temp_dir=$(mktemp -d) && git clone https://aur.archlinux.org/paru.git $temp_dir && cd $temp_dir && makepkg -si --noconfirm --noprogressbar && rm -rf $temp_dir)",
            "Clean Pacman Cache": "pkexec pacman -Sc --noconfirm",
            "Disable Bluetooth Autoswitch (Pipewire/WirePlumber)": "current=$(wpctl settings bluetooth.autoswitch-to-headset-profile); if [[ \"$current\" != *\"false\"* ]]; then wpctl settings --save bluetooth.autoswitch-to-headset-profile false; fi",
            "Trim SSD (Periodic)": "pkexec systemctl enable fstrim.timer"
        }

        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # List Widget to show tweaks
        self.list_widget = QListWidget()
        for tweak_name in self.tweaks.keys():
            item = QListWidgetItem(tweak_name)
            item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)

        # Apply Button
        self.apply_btn = QPushButton("Apply Selected Tweaks")
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #1793d1; 
                color: white; 
                font-weight: bold;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #34a6de; /* Lighter blue */
            }
            QPushButton:pressed {
                background-color: #0f6692; /* Darker blue when clicked */
            }
            """)
        self.apply_btn.clicked.connect(self.run_tweaks)

        # BEGIN Custom Back Button
        self.back_button_container = QFrame()
        self.back_button_container.setFixedSize(150, 45)

        self.frame_layout = QHBoxLayout(self.back_button_container)
        self.frame_layout.setContentsMargins(10, 0, 10, 0)
        self.frame_layout.setSpacing(5)  # Small gap between arrow and text

        # Remove the large manual spacing and stretch if you want them centered
        self.frame_layout.setAlignment(
            Qt.AlignCenter)  # Keeps group in the middle
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

        self.back_btn = QPushButton("←")  # Using an icon or arrow
        self.back_lbl = QLabel("Back")

        # Layout
        self.frame_layout.addWidget(self.back_btn)
        self.frame_layout.addSpacing(20)
        self.frame_layout.addWidget(self.back_lbl)
        self.frame_layout.addStretch()

        # Button press
        self.back_button_container.mousePressEvent = lambda event: self.go_back_to_setup()
        self.back_btn.clicked.connect(self.go_back_to_setup)
        # END Back Button

        # Main layout
        self.main_layout.addWidget(self.back_button_container)
        self.main_layout.addWidget(self.list_widget)
        self.main_layout.addWidget(self.apply_btn)

    def run_tweaks(self):
        selected_items = [
            self.list_widget.item(i).text()
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).checkState() == Qt.Checked
        ]

        if not selected_items:
            QMessageBox.warning(self, "No Selection",
                                "Please check at least one tweak to apply.")
            return

        for item_text in selected_items:
            cmd = self.tweaks[item_text]
            try:
                # We use shell=True because some commands use pipes/redirects
                subprocess.run(cmd, shell=True, check=True)
                print(f"Success: {item_text}")
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to run: {item_text}\n{e}")

        QMessageBox.information(
            self, "Finished", "Selected tweaks have been applied!")

    def go_back_to_setup(self):
        self.setup_window.show()  # Show the setup window
        self.hide()  # Hide the current window


# Example of how to run standalone
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ArchTweaks()
    window.show()
    sys.exit(app.exec_())
