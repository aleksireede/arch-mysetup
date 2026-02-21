#!/usr/bin/env python
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

# Ensure project root is importable when this file is run directly.
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from programs.apps_file import load_yaml
from gui.app_uninstaller import AppUninstaller
from gui.app_installer_window import ArchAppInstaller
from gui.setup_window import SetupWindow
from gui.advanced_tweaks import AdvancedTweaks

app = QApplication(sys.argv)

# Create the setup window first
setup_window = SetupWindow()
load_yaml()

# Reference to the other windows
app_installer_window = None
app_uninstaller_window = None
advanced_tweaks_window = None


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


def open_advanced_tweaks():
    global advanced_tweaks_window
    if advanced_tweaks_window is None:
        advanced_tweaks_window = AdvancedTweaks(setup_window)
    advanced_tweaks_window.show()
    setup_window.hide()


def main():
    # Configure the setup window to call other windows
    setup_window.open_installer.connect(open_app_installer)
    setup_window.open_uninstaller.connect(open_app_uninstaller)
    setup_window.open_advanced_tweaks.connect(open_advanced_tweaks)
    # Show setup window
    setup_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
