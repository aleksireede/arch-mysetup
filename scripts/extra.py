import os
import subprocess
from pathlib import Path

from programs.installer_logic import command_exists
from programs.text_editor import sudo_write_text
from text_writer import write_text

text_file_path = Path(__file__).parent.parent.resolve().joinpath("text_files")

# files
zeroconf_dest_path = Path.home().joinpath(".config", "pipewire", "pipewire.conf.d",
                                          "my-zeroconf-discover.conf").resolve()
airplay_dest_path = Path.home().joinpath(".config", "pipewire", "pipewire.conf.d", "raop-discover.conf").resolve()
xorg_keyboard_conf_path = Path("/etc/X11/xorg.conf.d/00-keyboard.conf")
pacman_mirrorlist_path = Path("/etc/pacman.d/mirrorlist")
pacman_reflector_config_path = Path("/etc/xdg/reflector/reflector.conf")

# texts
zeroconf_text = text_file_path.joinpath("zeroconf.txt").read_text()
airplay_text = text_file_path.joinpath("airplay.txt").read_text()
xorg_keyboard_conf_text = text_file_path.joinpath("xorg_keyboard_layout.txt").read_text()
reflector_text = text_file_path.joinpath("reflector.txt").read_text()


def bluetooth_no_autoswitch():
    bluetooth_string = subprocess.check_output(["wpctl", "settings", "bluetooth.autoswitch-to-headset-profile"])
    if not bluetooth_string == b'Value: false (Saved: false)\n':
        subprocess.run(["wpctl", "settings", "--save", "bluetooth.autoswitch-to-headset-profile", "false"])


def pacman_mirrorlist_update():
    """
    Update pacman mirrorlist
    """
    mirrorlist_text = subprocess.check_output(
        ["reflector", "--country", "Finland", "--latest", "10", "--age", "12", "--protocol", "https", "--sort", "rate"])
    sudo_write_text(pacman_mirrorlist_path, str(mirrorlist_text))


def reflector_service_timer():
    """
    Enable reflector service timer
    To automatically update pacman mirrorlist
    """
    if pacman_reflector_config_path.exists():
        return
    else:
        if not command_exists("reflector"):
            return
        write_config_file(pacman_reflector_config_path, reflector_text, True, True)
        command = ["pkexec", "systemctl", "enable", "--now", "reflector.timer"]
        subprocess.run(command)


def git_keystore():
    store_string = subprocess.check_output(["git", "config", "credential.helper"])
    if not store_string == b'store\n':
        subprocess.run(["git", "config", "--global", "credential.helper", "store"])
        print("Git config updated")
    else:
        print("Git config not updated")


def get_username():
    """
    Get username
    :return: username
    :rtype: str
    """
    return os.getlogin()


def write_config_file(file: Path, content: str, sudo=False, remove=False):
    """
    Write config file
    Returns True if file was written
    :rtype: bool
    :param file:
    :param content:
    :param sudo:
    :param remove:
    """
    if file.exists():
        return False
    else:
        if remove:
            file.unlink()
        if sudo:
            sudo_write_text(file, content)
        else:
            write_text(file, content)
        return True


def zeroconf_discover_pw():
    """
    Write zeroconf discover config file
    Then load zeroconf discover module
    """
    if zeroconf_dest_path.exists():
        return
    write_config_file(zeroconf_dest_path, zeroconf_text)
    subprocess.run(["pactl", "load-module", "module-zeroconf-discover"])


def airplay_discover_pw():
    """
    Write airplay discover config file
    Then load airplay discover module
    """
    if airplay_dest_path.exists():
        return
    write_config_file(airplay_dest_path, airplay_text)
    subprocess.run(["pactl", "load-module", "module-raop-discover"])


def xorg_keyboard_layout_fi():
    if xorg_keyboard_conf_path.exists():
        return
    write_config_file(xorg_keyboard_conf_path, xorg_keyboard_conf_text, True)
