import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QFrame,
)

try:
    from .ui_helpers import create_back_button
    from .theme import apply_dark_theme
except ImportError:
    from ui_helpers import create_back_button
    from theme import apply_dark_theme

from scripts.extra import (
    reflector_service_timer,
    git_keystore,
    zeroconf_discover_pw,
    airplay_discover_pw,
    xorg_keyboard_layout_fi,
)
from programs.text_editor import (
    write_bash_extra,
    enable_bash_extra,
    enable_multilib,
    pacman_enable_color,
)


class AdvancedTweaks(QMainWindow):
    def __init__(self, setup_window=None):
        super().__init__()
        self.system_tweak_list = None
        self.apply_tweaks_btn = None
        self.setup_window = setup_window
        self.setWindowTitle("Advanced Tweaks")
        self.setGeometry(100, 100, 940, 700)
        self.setMinimumSize(900, 660)
        self.system_tweaks = {
            "Enable Parallel Downloads (Pacman)": "pkexec sed -i 's/^#ParallelDownloads/ParallelDownloads/' /etc/pacman.conf",
            "Optimize Mirrorlist (Reflector)": "pkexec reflector --latest 50 --number 20 --sort delay --save /etc/pacman.d/mirrorlist",
            "Install Paru (Rust AUR Helper)": "pacman -Qi paru || (pkexec pacman -S --needed base-devel git && temp_dir=$(mktemp -d) && git clone https://aur.archlinux.org/paru.git $temp_dir && cd $temp_dir && makepkg -si --noconfirm --noprogressbar && rm -rf $temp_dir)",
            "Clean Pacman Cache": "pkexec pacman -Sc --noconfirm",
            "Disable Bluetooth Autoswitch (Pipewire/WirePlumber)": "current=$(wpctl settings bluetooth.autoswitch-to-headset-profile); if [[ \"$current\" != *\"false\"* ]]; then wpctl settings --save bluetooth.autoswitch-to-headset-profile false; fi",
            "Trim SSD (Periodic)": "pkexec systemctl enable fstrim.timer",
        }
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        apply_dark_theme(self)
        layout = QVBoxLayout(central)
        content_layout = QHBoxLayout()

        self.back_button_container, _, _, _ = create_back_button(self.go_back_to_setup)

        self.reflector_btn = QPushButton("Enable Reflector Timer")
        self.reflector_btn.clicked.connect(
            lambda: self.run_tweak(reflector_service_timer, "Reflector timer task completed.")
        )

        self.git_keystore_btn = QPushButton("Enable Git Credential Store")
        self.git_keystore_btn.clicked.connect(
            lambda: self.run_tweak(git_keystore, "Git credential helper task completed.")
        )

        self.zeroconf_btn = QPushButton("Enable PipeWire Zeroconf Discover")
        self.zeroconf_btn.clicked.connect(
            lambda: self.run_tweak(zeroconf_discover_pw, "Zeroconf discover task completed.")
        )

        self.airplay_btn = QPushButton("Enable PipeWire AirPlay Discover")
        self.airplay_btn.clicked.connect(
            lambda: self.run_tweak(airplay_discover_pw, "AirPlay discover task completed.")
        )

        self.keyboard_btn = QPushButton("Set Xorg Keyboard Layout (FI)")
        self.keyboard_btn.clicked.connect(
            lambda: self.run_tweak(xorg_keyboard_layout_fi, "Xorg keyboard layout task completed.")
        )

        self.bash_extra_file_btn = QPushButton("Install/Update ~/.bash_extra")
        self.bash_extra_file_btn.clicked.connect(
            lambda: self.run_tweak(write_bash_extra, "~/.bash_extra updated.")
        )

        self.bashrc_hook_btn = QPushButton("Enable ~/.bash_extra in ~/.bashrc")
        self.bashrc_hook_btn.clicked.connect(self.enable_bashrc_hook)

        self.multilib_btn = QPushButton("Enable Pacman Multilib")
        self.multilib_btn.clicked.connect(
            lambda: self.run_tweak(enable_multilib, "Multilib enable task completed.")
        )

        self.pacman_color_btn = QPushButton("Enable Pacman Color")
        self.pacman_color_btn.clicked.connect(
            lambda: self.run_tweak(pacman_enable_color, "Pacman color enable task completed.")
        )

        self.system_tweak_list = QListWidget()
        for tweak_name in self.system_tweaks.keys():
            item = QListWidgetItem(tweak_name)
            item.setCheckState(Qt.Unchecked)
            self.system_tweak_list.addItem(item)

        self.apply_tweaks_btn = QPushButton("Apply Selected System Tweaks")
        self.apply_tweaks_btn.clicked.connect(self.apply_selected_system_tweaks)

        quick_actions_container = QFrame()
        quick_actions_layout = QVBoxLayout(quick_actions_container)
        quick_actions_title = QLabel("Quick Actions")
        quick_actions_title.setStyleSheet("font-size: 16px; font-weight: 700;")
        quick_actions_layout.addWidget(quick_actions_title)
        quick_actions_layout.addWidget(self.reflector_btn)
        quick_actions_layout.addWidget(self.git_keystore_btn)
        quick_actions_layout.addWidget(self.zeroconf_btn)
        quick_actions_layout.addWidget(self.airplay_btn)
        quick_actions_layout.addWidget(self.keyboard_btn)
        quick_actions_layout.addWidget(self.bash_extra_file_btn)
        quick_actions_layout.addWidget(self.bashrc_hook_btn)
        quick_actions_layout.addWidget(self.multilib_btn)
        quick_actions_layout.addWidget(self.pacman_color_btn)
        quick_actions_layout.addStretch()

        system_tweaks_container = QFrame()
        system_tweaks_layout = QVBoxLayout(system_tweaks_container)
        system_tweaks_title = QLabel("Batch System Tweaks")
        system_tweaks_title.setStyleSheet("font-size: 16px; font-weight: 700;")
        system_tweaks_layout.addWidget(system_tweaks_title)
        system_tweaks_layout.addWidget(self.system_tweak_list)
        system_tweaks_layout.addWidget(self.apply_tweaks_btn)

        content_layout.addWidget(quick_actions_container, 3)
        content_layout.addWidget(system_tweaks_container, 2)

        layout.addWidget(self.back_button_container)
        layout.addSpacing(12)
        layout.addLayout(content_layout)

    def run_tweak(self, callback, success_message):
        try:
            callback()
            QMessageBox.information(self, "Done", success_message)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Action failed: {e}")

    def go_back_to_setup(self):
        if self.setup_window:
            self.setup_window.show()
        self.hide()

    def enable_bashrc_hook(self):
        try:
            changed = enable_bash_extra()
            if changed:
                QMessageBox.information(self, "Done", "Enabled ~/.bash_extra in ~/.bashrc and updated ~/.bash_profile template.")
            else:
                QMessageBox.information(self, "Already Enabled", "~/.bash_extra and ~/.bash_profile template are already enabled.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Action failed: {e}")

    def apply_selected_system_tweaks(self):
        selected_items = [
            self.system_tweak_list.item(i).text()
            for i in range(self.system_tweak_list.count())
            if self.system_tweak_list.item(i).checkState() == Qt.Checked
        ]

        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please check at least one tweak to apply.")
            return

        for item_text in selected_items:
            cmd = self.system_tweaks[item_text]
            try:
                subprocess.run(cmd, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Error", f"Failed to run: {item_text}\n{e}")
                return

        QMessageBox.information(self, "Finished", "Selected tweaks have been applied!")
