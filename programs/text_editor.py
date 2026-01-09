from pathlib import Path
import subprocess

# Arch / Pacman config
pacman_conf = Path(r"/etc/pacman.conf")
multilib_disabled = "#[multilib]\n#Include = /etc/pacman.d/mirrorlist"
multilib_enabled = "[multilib]\nInclude = /etc/pacman.d/mirrorlist"

# Bash config
bash_extra = Path(Path.home().joinpath(".bash_extra"))
bashrc = Path(Path.home().joinpath(".bashrc"))


def replacetext(file: Path, search_text: str, replace_text: str):
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


def write_text(file: Path, text: str):
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
    if bashrc.exists():
        print("Enabling extra bash configuration...")
        replacetext(bashrc,)

# Enable multilib in pacman.conf


def enable_multilib():
    if pacman_conf.exists():
        print("Enabling Multilib...")
        print(replacetext(pacman_conf, multilib_disabled, multilib_enabled))


# Disable multilib in pacman.conf
def disable_multilib():
    if pacman_conf.exists():
        print("Disabling Multilib...")
        print(replacetext(pacman_conf, multilib_enabled, multilib_disabled))


# Enable pacman colored output
def pacman_enable_color():
    if pacman_conf.exists():
        print("Enabling color in pacman...")
        print(replacetext(pacman_conf, "#Color", "Color"))


# Enable parallel downloads
def pacman_parallel_downloads():
    if pacman_conf.exists():
        print(replacetext(pacman_conf, "#ParallelDownloads=5", "ParallelDownloads=5"))
