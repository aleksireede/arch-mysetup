import os
import secrets
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


def command_exists(command):
    return shutil.which(command) is not None


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


def list_all_installed_apps():
    app_list = []
    app_list.extend(list_apps("pacman"))
    app_list.extend(list_apps("paru"))
    return app_list


def list_apps(method: str):
    cmd = []
    if method == "pacman":
        cmd = ["pacman", "-Qenq"]
    elif method == "paru":
        cmd = ["paru", "-Qemq"]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        applist = result.stdout.splitlines()
        return applist
    except subprocess.CalledProcessError:
        return []


def is_app_installed(app_name):
    """Check if an app is installed using pacman or paru."""
    try:
        subprocess.run(["pacman", "-Q", app_name],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        pass

    if command_exists("paru"):
        try:
            subprocess.run(["paru", "-Q", app_name],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            pass
    return False


def install_paru(sudo_password=None):
    """Install paru if not already installed."""
    script_path = Path(__file__).parent.parent.resolve().joinpath("scripts", "install_paru.sh")
    if command_exists("paru"):
        return True
    if sudo_password:
        temp_dir = Path(tempfile.mkdtemp(prefix="paru_", dir="/tmp"))
        askpass_file = Path(tempfile.mkstemp(prefix="arch_mysetup_askpass_", dir="/tmp")[1])
        try:
            subprocess.run(
                ["sudo", "-S", "-p", "", "-v"],
                input=sudo_password + "\n",
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            subprocess.run(
                ["sudo", "-S", "-p", "", "pacman", "-S", "--needed", "--noconfirm", "base-devel", "git", "rust"],
                input=sudo_password + "\n",
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            subprocess.run(
                ["git", "clone", "https://aur.archlinux.org/paru.git", str(temp_dir)],
                check=True
            )

            askpass_file.write_text(
                "#!/usr/bin/env python3\n"
                "import os\n"
                "print(os.environ.get('ARCH_MYSETUP_SUDO_PASSWORD', ''))\n"
            )
            os.chmod(askpass_file, 0o700)

            env = os.environ.copy()
            env["SUDO_ASKPASS"] = str(askpass_file)
            env["ARCH_MYSETUP_SUDO_PASSWORD"] = sudo_password
            env["PACMAN_AUTH"] = "sudo -A -p ''"

            subprocess.run(
                ["bash", "-lc", "makepkg -si --noconfirm --noprogressbar"],
                cwd=temp_dir,
                env=env,
                check=True
            )
            return command_exists("paru")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install Paru: {e}")
            return False
        finally:
            if askpass_file.exists():
                askpass_file.unlink()
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
    try:
        subprocess.run(["chmod", "+x", str(script_path)], check=True)
        paru = open_terminal(script_path)
        # Poll the process in a loop
        while True:
            exit_code = paru.poll()
            if exit_code is not None:
                if exit_code == 0:
                    print("Terminal command exited successfully")
                else:
                    print(f"Terminal command failed with exit code {exit_code}")
                break
            print("Terminal command is still running...")
            time.sleep(1)  # Check every second
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Paru: {e}")
        return False


# open a command in a terminal window
# now supports more terminals

def open_terminal(command):
    terminals = [
        ("kgx", ["--"], True),
        ("konsole", ["-e"], False),
        ("xfce4-terminal", ["-e"], False),
        ("xterm", ["-e"], False),
        ("alacritty", ["-e"], True),  # True: command is a list
        ("deepin-terminal", ["--run-script"], False),
        ("hyper", ["--"], False),
        ("putty", ["-e"], False),
        ("mate-terminal", ["--"], False),
    ]

    if isinstance(command, list):
        command_str = " ".join(command)
    else:
        command_str = command

    for term, args, use_list in terminals:
        if shutil.which(term):
            try:
                if use_list:
                    process = subprocess.Popen(
                        [term, *args, *command] if isinstance(command, list) else [term, *args, command])
                else:
                    process = subprocess.Popen([term, *args, command_str])
                return process
            except (OSError, ValueError, subprocess.SubprocessError):
                continue

    raise RuntimeError("No supported terminal emulator found")


def app_install(apps, command: str):
    if command == "paru":
        install_command= ["paru", "-S", "--skipreview", "--needed", "--quiet", "--color", "always"]
        return apps_helper(apps, install_command)
    elif command == "pacman":
        install_command = ["pkexec", "pacman", "-S", "--needed", "--quiet", "--color", "always"]
        return apps_helper(apps, install_command)
    return None

def remove_apps(apps, command: str):
    remove_command = []
    if command == "paru":
        remove_command.append("paru")
    elif command == "pacman":
        remove_command.append("pkexec")
        remove_command.append("pacman")
    remove_command.extend(["-Rns", "--color", "always"])
    return apps_helper(apps, remove_command)


def apps_helper(apps, command):
    try:
        if type(apps) is list:
            return open_terminal([*command, *apps])
        else:
            return open_terminal([*command, apps])
    except Exception as e:
        print(e)
        return False


def add_samba_drive(share_path, mount_point, username, password, sudo_password=None):
    """Add a Samba network drive to fstab and create .smbcredentials."""
    cred_file = generate_unique_cred_path()

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
        script_path = Path(__file__).parent.parent / "scripts" / "setup_samba.sh"
        if sudo_password:
            subprocess.run(
                ["sudo", "-S", str(script_path), mount_point, share_path, str(cred_file)],
                input=sudo_password + "\n",
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        else:
            subprocess.run(["pkexec", script_path, mount_point, share_path, str(cred_file)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to setup Samba drive: {e}")
        return False

    return True


def generate_unique_cred_path(root_dir=None, max_attempts=100):
    """
    Create a unique random subdirectory under root_dir and return its
    .smbcredentials file path.
    """
    if root_dir is None:
        root_dir = Path.home().joinpath(".config", "arch-mysetup", "credentials")
    root_path = Path(root_dir)
    root_path.mkdir(mode=0o700, parents=True, exist_ok=True)
    for _ in range(max_attempts):
        random_name = f"smbcred_{secrets.token_hex(6)}"
        candidate_dir = root_path / random_name
        try:
            # Atomic create so an existing name is never reused.
            candidate_dir.mkdir(mode=0o700, parents=False, exist_ok=False)
            return candidate_dir / ".smbcredentials"
        except FileExistsError:
            continue
        except PermissionError as e:
            raise RuntimeError(f"Permission denied while creating {candidate_dir}") from e

    raise RuntimeError("Failed to allocate a unique credentials path")
