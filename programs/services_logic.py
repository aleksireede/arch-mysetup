import shutil
import subprocess
from pathlib import Path


MANAGED_USER_SERVICES = [
    {
        "key": "syncthing",
        "name": "Syncthing",
        "unit": "syncthing.service",
    },
    {
        "key": "ollama",
        "name": "Ollama",
        "unit": "ollama.service",
    },
]


def _run_systemctl_user(*args):
    return subprocess.run(
        ["systemctl", "--user", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def _daemon_reload_user():
    result = _run_systemctl_user("daemon-reload")
    if result.returncode != 0:
        error_text = result.stderr.strip() or "Failed to reload user systemd daemon"
        raise RuntimeError(error_text)


def _read_systemctl_user_state(*args):
    result = _run_systemctl_user(*args)
    stdout = result.stdout.strip()
    if result.returncode != 0:
        if stdout:
            return stdout
        stderr = result.stderr.strip()
        if stderr:
            return f"error: {stderr}"
        return "unknown"
    return stdout or "unknown"


def _ensure_ollama_user_service(unit_name):
    if unit_name != "ollama.service":
        return

    user_systemd_dir = Path.home() / ".config" / "systemd" / "user"
    service_path = user_systemd_dir / unit_name
    if service_path.exists():
        return

    ollama_path = shutil.which("ollama")
    if not ollama_path:
        raise RuntimeError("`ollama` binary was not found in PATH.")

    user_systemd_dir.mkdir(parents=True, exist_ok=True)
    service_path.write_text(
        "\n".join(
            [
                "[Unit]",
                "Description=Ollama",
                "After=default.target",
                "",
                "[Service]",
                f"ExecStart={ollama_path} serve",
                "Restart=always",
                "RestartSec=3",
                "",
                "[Install]",
                "WantedBy=default.target",
                "",
            ]
        ),
        encoding="utf-8",
    )
    _daemon_reload_user()


def get_managed_user_services():
    services = []
    for service in MANAGED_USER_SERVICES:
        services.append(
            {
                **service,
                "enabled_state": _read_systemctl_user_state("is-enabled", service["unit"]),
                "active_state": _read_systemctl_user_state("is-active", service["unit"]),
            }
        )
    return services


def start_user_service(unit_name):
    _ensure_ollama_user_service(unit_name)
    result = _run_systemctl_user("start", unit_name)
    if result.returncode != 0:
        error_text = result.stderr.strip() or f"Failed to start {unit_name}"
        raise RuntimeError(error_text)


def enable_user_service(unit_name):
    _ensure_ollama_user_service(unit_name)
    result = _run_systemctl_user("enable", unit_name)
    if result.returncode != 0:
        error_text = result.stderr.strip() or f"Failed to enable {unit_name}"
        raise RuntimeError(error_text)
