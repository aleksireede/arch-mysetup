#!/usr/bin/env python
from PyQt5.QtWidgets import QApplication
import sys
from pathlib import Path

parent_dir = str(Path(__file__).resolve().parent.parent.joinpath("gui"))
sys.path.append(parent_dir)

from app_uninstaller import AppUninstaller
from app_installer_window import ArchAppInstaller
from setup_window import SetupWindow
from arch_tweaks import ArchTweaks

app = QApplication(sys.argv)

# Create the setup window first
setup_window = SetupWindow()

# Reference to the other windows
app_installer_window = None
app_uninstaller_window = None
tweaks_window = None


def open_app_installer():
    global app_installer_window
    if app_installer_window is None:
        app_installer_window = ArchAppInstaller(setup_window)
    app_installer_window.show()
    setup_window.hide()


def open_app_uninstaller():
    global app_uninstaller_window
    if app_uninstaller_window is None:
        app_uninstaller_window = AppUninstaller(setup_window)
    app_uninstaller_window.show()
    setup_window.hide()


def open_tweaks():
    global tweaks_window
    if tweaks_window is None:
        tweaks_window = ArchTweaks(setup_window)
    tweaks_window.show()
    setup_window.hide()


def main():
    # Configure the setup window to call other windows
    setup_window.open_installer.connect(open_app_installer)
    setup_window.open_uninstaller.connect(open_app_uninstaller)
    setup_window.open_tweaks.connect(open_tweaks)
    # Show setup window
    setup_window.show()

    sys.exit(app.exec_())


# :todo fix yaml not adding apps
if __name__ == "__main__":
    main()
