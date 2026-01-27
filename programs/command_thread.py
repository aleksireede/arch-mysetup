import sys
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

class CommandThread(QThread):
    finished = pyqtSignal(bool, str)  # Signal to emit when the command finishes

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            result = subprocess.run(
                self.command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.finished.emit(True, result.stdout)
        except subprocess.CalledProcessError as e:
            self.finished.emit(False, e.stderr)
        except Exception as e:
            self.finished.emit(False, str(e))
