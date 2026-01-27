import subprocess
from pathlib import Path

from scripts.text_writer import write_text

# Arch / Pacman config
pacman_conf = Path(r"/etc/pacman.conf")
multilib_disabled = "#[multilib]\n#Include = /etc/pacman.d/mirrorlist"
multilib_enabled = "[multilib]\nInclude = /etc/pacman.d/mirrorlist"

# Bash config
bash_extra_path = Path(Path.home().joinpath(".bash_extra"))
bashrc_path = Path(Path.home().joinpath(".bashrc"))
bashrc_extra_text = 'if [ -f ~/.bash_extra ]; then\n. ~/.bash_extra\nfi")'
bash_extra_text = Path(__file__).parent.parent.resolve().joinpath("text_files/bash_extra.txt").read_text()


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
    # check that the bashrc config exists and that the text is not already enabled
    if bashrc_path.exists() and bashrc_extra_text not in bashrc_path.read_text():
        print("Enabling extra bash configuration...")
        write_text(bashrc_path, bashrc_extra_text)
        return True
    else:
        return False


def write_bash_extra():
    """
    Enables extra bash configuration to add the bash extra file
    If it already exists then it is updated.
    :rtype: None
    """
    # write text to bash_extra if not exists from built-in file /text_files/bash_extra.txt
    if not bash_extra_path.exists():
        print("Enabling extra bash configuration...")
        write_text(bash_extra_path, bash_extra_text)
    else:
        # we need to remove the file to update it
        print("Updating extra bash configuration...")
        bash_extra_path.unlink()
        write_text(bash_extra_path, bash_extra_text)


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
