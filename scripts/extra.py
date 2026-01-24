import subprocess
from pathlib import Path

from text_writer import write_text


def bluetooth_no_autoswitch():
    subprocess.run(["wpctl", "settings", "--save", "bluetooth.autoswitch-to-headset-profile", "false"])


def git_keystore():
    subprocess.run(["git", "config", "--global", "credential.helper", "store"])


def zeroconf_discover_pw():
    out_file = Path.home().joinpath(".config", "pipewire", "pipewire.conf.d", "my-zeroconf-discover.conf").resolve()
    in_file = Path(__file__).parent.parent.resolve().joinpath("text_files", "zeroconf.txt")
    text = in_file.read_text()
    if not out_file.exists():
        write_text(out_file, text)
