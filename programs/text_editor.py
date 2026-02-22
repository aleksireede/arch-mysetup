import subprocess
from pathlib import Path

from programs.config import (
    PACMAN_CONF_PATH,
    BASH_EXTRA_PATH,
    BASHRC_PATH,
    FISH_CONFIG_PATH,
    BASH_EXTRA_VERSION,
    BASH_EXTRA_TEMPLATE_PATH,
)

# Arch / Pacman config
pacman_conf = PACMAN_CONF_PATH
multilib_disabled = "#[multilib]\n#Include = /etc/pacman.d/mirrorlist"
multilib_enabled = "[multilib]\nInclude = /etc/pacman.d/mirrorlist"

# Bash config
bash_extra_path = BASH_EXTRA_PATH
bashrc_path = BASHRC_PATH
fish_config_path = FISH_CONFIG_PATH
bashrc_extra_text = 'if [ -f ~/.bash_extra ]; then\n. ~/.bash_extra\nfi'
bash_extra_version = BASH_EXTRA_VERSION
_bash_extra_body = BASH_EXTRA_TEMPLATE_PATH.read_text().rstrip()
bash_extra_text = (
    f"# Managed by arch-mysetup\n"
    f"# arch-mysetup-bash-extra-version: {bash_extra_version}\n\n"
    f"{_bash_extra_body}\n"
)


# todo: find text and then read the whole line to edit eg. ParallelDownload=5 to edit the number
def check_if_text_exists(file: Path, search_text: str):
    """
    Checks if text exists in file.
    :param file: the file to check
    :param search_text: the text to search for
    """
    data = file.read_text()

    if search_text not in data:
        print(f"Text not found: '{search_text}' — skipping.")
        return False
    else:
        return True


def sudo_replace_text(file: Path, search_text: str, replace_text: str):
    script_path = Path(__file__).resolve().parent / \
                  "../scripts/text_writer.py"
    subprocess.run([
        "pkexec",
        "python3",
        str(script_path),
        file,
        search_text,
        replace_text
    ], check=True)


def sudo_write_text(file: Path, text: str):
    script_path = Path(__file__).resolve().parent / \
                  "../scripts/text_writer.py"
    subprocess.run([
        "pkexec",
        "python3",
        str(script_path),
        file,
        text
    ], check=True)


def enable_bash_extra():
    """
    Enables extra bash configuration to add the bash_extra file

    Returns True if extra bash configuration was enabled
    :rtype: bool
    """
    changed = False

    # Enable ~/.bash_extra source line in ~/.bashrc
    if not bashrc_path.exists():
        bashrc_path.touch()
    bashrc_data = bashrc_path.read_text()
    if bashrc_extra_text not in bashrc_data:
        with open(bashrc_path, "a") as f:
            f.write("\n" + bashrc_extra_text + "\n")
        changed = True

    # Enable ~/.bash_extra source line in ~/.config/fish/config.fish
    fish_config_path.parent.mkdir(parents=True, exist_ok=True)
    if not fish_config_path.exists():
        fish_config_path.touch()
    fish_config_data = fish_config_path.read_text()
    if bashrc_extra_text not in fish_config_data:
        with open(fish_config_path, "a") as f:
            f.write("\n" + bashrc_extra_text + "\n")
        changed = True

    if changed:
        print("Enabled bash extra in ~/.bashrc and ~/.config/fish/config.fish")
    return changed


def write_bash_extra():
    """
    Enables extra bash configuration to add the bash extra file
    If it already exists then it is updated.
    :rtype: None
    """
    # Backwards-compatible wrapper for full overwrite updates.
    update_bash_extra()


def update_bash_extra():
    """
    Overwrite ~/.bash_extra with the latest managed template and version header.
    :rtype: None
    """
    if bash_extra_path.exists():
        print(f"Updating ~/.bash_extra to version {bash_extra_version}...")
    else:
        print(f"Installing ~/.bash_extra version {bash_extra_version}...")
    bash_extra_path.write_text(bash_extra_text)


def check_multilib():
    """
    Checks if multilib is enabled.
    Returns True if multilib configuration was enabled
    :rtype: bool
    """
    if pacman_conf.exists():
        if multilib_enabled in pacman_conf.read_text():
            return True
        else:
            return False
    return None


def enable_multilib():
    # Enable multilib in pacman.conf
    if pacman_conf.exists():
        print("Enabling Multilib...")
        print(sudo_replace_text(pacman_conf, multilib_disabled, multilib_enabled))


def disable_multilib():
    # Disable multilib in pacman.conf
    if pacman_conf.exists():
        print("Disabling Multilib...")
        print(sudo_replace_text(pacman_conf, multilib_enabled, multilib_disabled))


def check_pacman_color():
    """
    Check whether pacman color is enabled.
    Returns True if pacman color was enabled
    :rtype: bool
    """
    if pacman_conf.exists():
        if "#Color" in pacman_conf.read_text():
            return False
        else:
            return True
    return None


def pacman_enable_color():
    # Enable pacman colored output
    if pacman_conf.exists():
        print("Enabling color in pacman...")
        print(sudo_replace_text(pacman_conf, "#Color", "Color"))


def pacman_disable_color():
    # Disable pacman colored output
    if pacman_conf.exists():
        print("Enabling color in pacman...")
        print(sudo_replace_text(pacman_conf, "Color", "#Color"))


def pacman_check_parallel_downloads():
    """
    Checks if pacman parallel downloads is enabled.
    Returns True if pacman parallel downloads was enabled
    :rtype: bool
    """
    if pacman_conf.exists():
        if "#ParallelDownloads=5" in pacman_conf.read_text():
            return False
        else:
            return True
    return None


def pacman_enable_parallel_downloads():
    # Enable parallel downloads
    if pacman_conf.exists():
        print(sudo_replace_text(pacman_conf, "#ParallelDownloads=5", "ParallelDownloads=5"))


def pacman_disable_parallel_downloads():
    # Disable parallel downloads
    if pacman_conf.exists():
        print(sudo_replace_text(pacman_conf, "ParallelDownloads=5", "#ParallelDownloads=5"))
