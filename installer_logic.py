import subprocess
import json
import os

def check_if_installed(command):
    """Check if a command is available in the system."""
    try:
        subprocess.run(["which", command], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def is_app_installed(app_name):
    """Check if an app is installed using pacman, paru, or flatpak."""
    try:
        subprocess.run(["pacman", "-Q", app_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        pass

    if check_if_installed("paru"):
        try:
            subprocess.run(["paru", "-Q", app_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            pass

    if check_if_installed("flatpak"):
        try:
            subprocess.run(["flatpak", "list", "--app", "--columns=application", app_name],
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
            ["pkexec", "bash", "-c", "cd /opt && git clone https://aur.archlinux.org/paru.git && cd paru && makepkg -si --noconfirm"],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Paru: {e}")
        return False

def install_flatpak():
    """Install flatpak if not already installed."""
    if check_if_installed("flatpak"):
        return True
    try:
        subprocess.run(["pkexec", "pacman", "-S", "--noconfirm", "flatpak"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Flatpak: {e}")
        return False

def install_app(app_name):
    """Try to install an app using pacman, paru, or flatpak in order."""
    try:
        subprocess.run(["pkexec", "pacman", "-S", "--noconfirm", app_name], check=True)
        return True
    except subprocess.CalledProcessError:
        try:
            if check_if_installed("paru"):
                subprocess.run(["paru", "-S", "--noconfirm", app_name], check=True)
                return True
        except subprocess.CalledProcessError:
            try:
                if check_if_installed("flatpak"):
                    subprocess.run(["flatpak", "install", "-y", "flathub", app_name], check=True)
                    return True
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {app_name} with all methods: {e}")
                return False
    return False

def load_apps_from_json():
    """Load the list of apps from a JSON file."""
    if not os.path.exists("apps.json"):
        default_apps = [
            "firefox", "vlc", "gimp", "libreoffice", "steam",
            "spotify", "discord", "visual-studio-code", "python", "git", "zsh"
        ]
        with open("apps.json", "w") as f:
            json.dump(default_apps, f)
        return default_apps
    else:
        with open("apps.json", "r") as f:
            return json.load(f)

def save_selections(selections):
    """Save the selected apps to a settings file."""
    with open("settings.json", "w") as f:
        json.dump(selections, f)

def load_selections():
    """Load the selected apps from the settings file."""
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            return json.load(f)
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
        subprocess.run(["pkexec", script_path, mount_point, share_path, cred_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to setup Samba drive: {e}")
        return False

    return True
