import subprocess


MANAGED_SERVICES = [
    {
        "key": "syncthing",
        "name": "Syncthing",
        "unit": "syncthing.service",
        "scope": "user",
    },
    {
        "key": "fstrim",
        "name": "Filesystem Trim Timer",
        "unit": "fstrim.timer",
        "scope": "system",
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


def _run_systemctl_system(*args):
    return subprocess.run(
        ["sudo", "-n", "systemctl", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def _run_systemctl(service, *args):
    if service.get("scope") == "system":
        return _run_systemctl_system(*args)
    return _run_systemctl_user(*args)


def _read_systemctl_state(service, *args):
    result = _run_systemctl(service, *args)
    stdout = result.stdout.strip()
    if result.returncode != 0:
        if stdout:
            return stdout
        stderr = result.stderr.strip()
        if stderr:
            return f"error: {stderr}"
        return "unknown"
    return stdout or "unknown"


def has_system_services():
    return any(service.get("scope") == "system" for service in MANAGED_SERVICES)


def validate_sudo_password(password):
    result = subprocess.run(
        ["sudo", "-S", "-v"],
        input=f"{password}\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        error_text = result.stderr.strip() or "Failed to authenticate sudo session"
        raise RuntimeError(error_text)


def invalidate_sudo_timestamp():
    subprocess.run(
        ["sudo", "-K"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def is_sudo_auth_error(error_message):
    normalized = (error_message or "").strip().lower()
    return any(
        token in normalized
        for token in (
            "sudo",
            "a password is required",
            "authentication",
            "not in the sudoers",
        )
    )


def get_managed_services():
    services = []
    for service in MANAGED_SERVICES:
        services.append(
            {
                **service,
                "enabled_state": _read_systemctl_state(service, "is-enabled", service["unit"]),
                "active_state": _read_systemctl_state(service, "is-active", service["unit"]),
            }
        )
    return services


def start_service(service):
    result = _run_systemctl(service, "start", service["unit"])
    if result.returncode != 0:
        error_text = result.stderr.strip() or f"Failed to start {service['unit']}"
        raise RuntimeError(error_text)


def enable_service(service):
    result = _run_systemctl(service, "enable", service["unit"])
    if result.returncode != 0:
        error_text = result.stderr.strip() or f"Failed to enable {service['unit']}"
        raise RuntimeError(error_text)
