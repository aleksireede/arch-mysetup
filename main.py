#!/usr/bin/env python
import sys
sys.path.append("gui")
from setup_window import SetupWindow
from app_installer_window import ArchAppInstaller
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)

    # Create the setup window first
    setup_window = SetupWindow()

    # Reference to the app installer window
    app_installer_window = None
    
    def open_app_installer():
        nonlocal app_installer_window
        if app_installer_window is None:
            app_installer_window = ArchAppInstaller(setup_window)
        app_installer_window.show()
        setup_window.hide()  # Hide the setup window when opening the installer

    # Configure the setup window to call open_app_installer
    setup_window.open_installer.connect(open_app_installer)
    setup_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
