import sys
from PyQt5.QtWidgets import QApplication
from setup_window import SetupWindow
from app_installer_window import ArchAppInstaller

def main():
    app = QApplication(sys.argv)

    app_installer_window = None  # persistent reference

    def open_app_installer():
        nonlocal app_installer_window
        app_installer_window = ArchAppInstaller()
        app_installer_window.show()

    setup_window = SetupWindow(open_app_installer)
    setup_window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
