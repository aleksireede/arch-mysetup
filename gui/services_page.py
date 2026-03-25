from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from programs.services_logic import (
    enable_user_service,
    get_managed_user_services,
    start_user_service,
)

try:
    from .ui_helpers import create_back_button
    from .theme import configure_main_window, create_page_header
except ImportError:
    from ui_helpers import create_back_button
    from theme import configure_main_window, create_page_header


class ServicesWorker(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def run(self):
        try:
            self.finished.emit(get_managed_user_services())
        except Exception as e:
            self.error.emit(str(e))


class ServiceActionWorker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, action, unit_name):
        super().__init__()
        self.action = action
        self.unit_name = unit_name

    def run(self):
        try:
            self.action(self.unit_name)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class ServicesPage(QMainWindow):
    def __init__(self, setup_window=None):
        super().__init__()
        self.setup_window = setup_window
        self.back_button_container = None
        self.thread = None
        self.worker = None
        self.action_thread = None
        self.action_worker = None
        self.refresh_button = None
        self.status_label = None
        self.service_rows = {}

        self.setWindowTitle("Services")
        configure_main_window(self)
        self.init_ui()
        self.refresh_services_async()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.back_button_container, _, _, _ = create_back_button(self.go_back_to_setup)
        header_widget = create_page_header(self.back_button_container, "Services")

        self.status_label = QLabel("Loading user services...")
        self.status_label.setObjectName("syncStatusLabel")

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_services_async)
        self.refresh_button.setFixedWidth(200)

        services_layout = QVBoxLayout()
        for service_key, service_name in (
            ("syncthing", "Syncthing"),
            ("ollama", "Ollama"),
        ):
            card = QFrame()
            card_layout = QVBoxLayout(card)

            name_label = QLabel(service_name)
            name_label.setStyleSheet("font-size: 18px; font-weight: 600;")
            state_label = QLabel("Loading...")

            button_row = QHBoxLayout()
            start_button = QPushButton("Start")
            enable_button = QPushButton("Enable")
            start_button.setFixedWidth(140)
            enable_button.setFixedWidth(140)
            button_row.addWidget(start_button)
            button_row.addWidget(enable_button)
            button_row.addStretch()

            card_layout.addWidget(name_label)
            card_layout.addWidget(state_label)
            card_layout.addLayout(button_row)

            services_layout.addWidget(card)

            self.service_rows[service_key] = {
                "state_label": state_label,
                "start_button": start_button,
                "enable_button": enable_button,
            }

        self.service_rows["syncthing"]["start_button"].clicked.connect(
            lambda: self.run_service_action(start_user_service, "syncthing.service", "Starting Syncthing...")
        )
        self.service_rows["syncthing"]["enable_button"].clicked.connect(
            lambda: self.run_service_action(enable_user_service, "syncthing.service", "Enabling Syncthing...")
        )
        self.service_rows["ollama"]["start_button"].clicked.connect(
            lambda: self.run_service_action(start_user_service, "ollama.service", "Starting Ollama...")
        )
        self.service_rows["ollama"]["enable_button"].clicked.connect(
            lambda: self.run_service_action(enable_user_service, "ollama.service", "Enabling Ollama...")
        )

        layout.addWidget(header_widget)
        layout.addSpacing(12)
        layout.addWidget(self.status_label)
        layout.addLayout(services_layout)
        layout.addWidget(self.refresh_button)
        layout.addStretch()

    def go_back_to_setup(self):
        if self.setup_window:
            self.setup_window.show()
        self.hide()

    def refresh_services_async(self):
        if self.thread and self.thread.isRunning():
            return

        self.set_controls_enabled(False)
        self.status_label.setText("Refreshing user services...")
        self.set_all_state_labels("Refreshing...")

        self.thread = QThread()
        self.worker = ServicesWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_services_loaded)
        self.worker.error.connect(self.on_services_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.cleanup_thread)
        self.thread.start()

    def on_services_loaded(self, services):
        self.set_controls_enabled(True)
        self.status_label.setText("User services are ready.")
        for service in services:
            row = self.service_rows.get(service["key"])
            if row is None:
                continue
            row["state_label"].setText(
                f"Unit: {service['unit']} | Enabled: {service['enabled_state']} | Active: {service['active_state']}"
            )

    def on_services_error(self, error_message):
        self.set_controls_enabled(True)
        self.set_all_state_labels("Status unavailable.")
        self.status_label.setText(f"Could not load services: {error_message}")

    def cleanup_thread(self):
        self.thread = None
        self.worker = None

    def run_service_action(self, action, unit_name, status_message):
        if self.action_thread and self.action_thread.isRunning():
            return

        self.set_controls_enabled(False)
        self.status_label.setText(status_message)

        self.action_thread = QThread()
        self.action_worker = ServiceActionWorker(action, unit_name)
        self.action_worker.moveToThread(self.action_thread)
        self.action_thread.started.connect(self.action_worker.run)
        self.action_worker.finished.connect(self.on_service_action_finished)
        self.action_worker.error.connect(self.on_service_action_error)
        self.action_worker.finished.connect(self.action_thread.quit)
        self.action_worker.finished.connect(self.action_worker.deleteLater)
        self.action_worker.error.connect(self.action_thread.quit)
        self.action_worker.error.connect(self.action_worker.deleteLater)
        self.action_thread.finished.connect(self.action_thread.deleteLater)
        self.action_thread.finished.connect(self.cleanup_action_thread)
        self.action_thread.start()

    def on_service_action_finished(self):
        self.status_label.setText("Service action completed.")
        self.refresh_services_async()

    def on_service_action_error(self, error_message):
        self.set_controls_enabled(True)
        self.status_label.setText(f"Service action failed: {error_message}")
        QMessageBox.critical(self, "Service Error", error_message)

    def cleanup_action_thread(self):
        self.action_thread = None
        self.action_worker = None

    def set_controls_enabled(self, enabled):
        self.refresh_button.setEnabled(enabled)
        for row in self.service_rows.values():
            row["start_button"].setEnabled(enabled)
            row["enable_button"].setEnabled(enabled)

    def set_all_state_labels(self, text):
        for row in self.service_rows.values():
            row["state_label"].setText(text)

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(3000)
        if self.action_thread and self.action_thread.isRunning():
            self.action_thread.quit()
            self.action_thread.wait(3000)
        super().closeEvent(event)
