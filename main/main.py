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
from gui.apps_page import AppsPage
from gui.browsers_page import BrowsersPage
from gui.dev_tools_page import DevToolsPage
from gui.games_page import GamesPage
from gui.setup_window import SetupWindow
from gui.advanced_tweaks import AdvancedTweaks
from gui.services_page import ServicesPage

app = QApplication(sys.argv)

# Create the setup window first
setup_window = SetupWindow()
load_yaml()

# Reference to the other windows
app_installer_window = None
app_uninstaller_window = None
advanced_tweaks_window = None
apps_page_window = None
services_page_window = None
games_page_window = None
dev_tools_page_window = None
browsers_page_window = None


def ensure_apps_page():
    global apps_page_window
    if apps_page_window is None:
        apps_page_window = AppsPage(setup_window)
    return apps_page_window


def open_app_installer():
    global app_installer_window
    apps_page = ensure_apps_page()
    if app_installer_window is None:
        app_installer_window = ArchAppInstaller(apps_page)
    app_installer_window.show()
    setup_window.hide()


def open_app_uninstaller():
    global app_uninstaller_window
    apps_page = ensure_apps_page()
    if app_uninstaller_window is None:
        app_uninstaller_window = AppUninstaller(apps_page)
    app_uninstaller_window.show()
    setup_window.hide()


def open_advanced_tweaks():
    global advanced_tweaks_window
    if advanced_tweaks_window is None:
        advanced_tweaks_window = AdvancedTweaks(setup_window)
    advanced_tweaks_window.show()
    setup_window.hide()


def open_apps_page():
    apps_page = ensure_apps_page()
    apps_page.show()
    setup_window.hide()


def open_services_page():
    global services_page_window
    if services_page_window is None:
        services_page_window = ServicesPage(setup_window)
    services_page_window.show()
    setup_window.hide()


def open_games_page():
    global games_page_window
    if games_page_window is None:
        games_page_window = GamesPage(setup_window)
    games_page_window.show()
    setup_window.hide()


def open_dev_tools_page():
    global dev_tools_page_window
    if dev_tools_page_window is None:
        dev_tools_page_window = DevToolsPage(setup_window)
    dev_tools_page_window.show()
    setup_window.hide()


def open_browsers_page():
    global browsers_page_window
    if browsers_page_window is None:
        browsers_page_window = BrowsersPage(setup_window)
    browsers_page_window.show()
    setup_window.hide()


def main():
    # Configure the setup window to call other windows
    setup_window.open_installer.connect(open_app_installer)
    setup_window.open_uninstaller.connect(open_app_uninstaller)
    setup_window.open_advanced_tweaks.connect(open_advanced_tweaks)
    setup_window.open_apps_page.connect(open_apps_page)
    setup_window.open_services_page.connect(open_services_page)
    setup_window.open_games_page.connect(open_games_page)
    setup_window.open_dev_tools_page.connect(open_dev_tools_page)
    setup_window.open_browsers_page.connect(open_browsers_page)
    # Show setup window
    setup_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
