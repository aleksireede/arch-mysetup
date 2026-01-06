import shutil
import subprocess
import json
import os


def command_exists(cmd):
    return shutil.which(cmd) is not None


def detect_install_method(app_name):
    """
    Decide how the app should be installed.
    Returns: "pacman", "paru" or None
    """

    # Check official repos
    try:
        subprocess.run(
            ["pacman", "-Si", app_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return "pacman"
    except subprocess.CalledProcessError:
        pass

    # Check AUR via paru
    if command_exists("paru"):
        try:
            subprocess.run(
                ["paru", "-Si", app_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return "paru"
        except subprocess.CalledProcessError:
            pass
    return None


def check_if_installed(command):
    """Check if a command is available in the system."""
    try:
        subprocess.run(["which", command], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False


def is_app_installed(app_name):
    """Check if an app is installed using pacman or paru."""
    try:
        subprocess.run(["pacman", "-Q", app_name],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        pass

    if check_if_installed("paru"):
        try:
            subprocess.run(["paru", "-Q", app_name],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            pass
    return False


def install_paru():
    """Install paru if not already installed."""
    if check_if_installed("paru"):
        return True
    try:
        subprocess.run(
            ["pkexec", "bash", "-c",
                "cd /opt && git clone https://aur.archlinux.org/paru.git && cd paru && makepkg -si --noconfirm"],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Paru: {e}")
        return False


def open_terminal(command):
    terminals = [
        ("kgx", ["--"]),
        ("konsole", ["-e"]),
        ("xfce4-terminal", ["-e"]),
        ("xterm", ["-e"]),
    ]

    for term, args in terminals:
        if shutil.which(term):
            subprocess.Popen([term, *args, *command])
            return

    raise RuntimeError("No supported terminal emulator found")


def install_app(app_name):
    method = detect_install_method(app_name)

    if not method:
        print(f"No install source found for {app_name}")
        return False

    try:
        if method == "pacman":
            open_terminal(
                ["pkexec", "pacman", "-S", "--noconfirm", app_name]
            )

        elif method == "paru":
            open_terminal(
                [
                    "paru",
                    "-S",
                    "--noconfirm",
                    "--skipreview",
                    "--needed",
                    app_name
                ]
            )

        print(f"{app_name} installed successfully using {method}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Installation failed: {e}")
        return False


def load_apps_from_json():
    if not os.path.exists("apps.json"):
        # If the file doesn't exist, return empty list
        return []

    with open("apps.json", "r") as f:
        try:
            data = json.load(f)
            if not isinstance(data, list):
                # Ensure it's a list
                return []
            return data
        except json.JSONDecodeError:
            # If the file is empty or invalid, return empty list
            return []


def add_samba_drive(share_path, mount_point, username, password):
    """Add a Samba network drive to fstab and create .smbcredentials."""
    home_dir = os.path.expanduser("~")
    cred_file = os.path.join(home_dir, ".smbcredentials")

    # Create credentials file
    try:
        with open(cred_file, "w") as f:
            f.write(f"username={username}\npassword={password}\n")
        os.chmod(cred_file, 0o600)
    except Exception as e:
        print(f"Failed to write credentials: {e}")
        return False

    # Run the setup script with pkexec
    try:
        script_path = os.path.join(os.path.dirname(__file__), "setup_samba.sh")
        subprocess.run(["pkexec", script_path, mount_point,
                       share_path, cred_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to setup Samba drive: {e}")
        return False

    return True
