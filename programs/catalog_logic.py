import re
import urllib.request
from pathlib import Path

import yaml

from programs.config import QUESTION_MARK_ICON_PATH
from programs.installer_logic import (
    app_install,
    get_install_method_from_source,
    is_app_installed,
    remove_apps,
)


def load_catalog_entries(catalog_path: Path):
    if not catalog_path.exists():
        return []

    with open(catalog_path, "r", encoding="utf-8") as catalog_file:
        data = yaml.safe_load(catalog_file) or []

    entries = []
    for entry in data:
        if not isinstance(entry, dict) or not entry.get("name"):
            continue
        entries.append(
            {
                "name": entry["name"],
                "title": entry.get("title", entry["name"]),
                "description": entry.get("description", ""),
                "source": entry.get("source"),
                "icon_url": entry.get("icon_url"),
            }
        )
    return entries


def get_catalog_icon_path(entry, icon_dir: Path):
    icon_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", entry["name"].lower()).strip("-")
    return icon_dir.joinpath(f"{slug}.png")


def ensure_catalog_icon(entry, icon_dir: Path):
    icon_path = get_catalog_icon_path(entry, icon_dir)
    if icon_path.exists():
        return icon_path

    icon_url = entry.get("icon_url")
    if not icon_url:
        return QUESTION_MARK_ICON_PATH

    try:
        request = urllib.request.Request(
            icon_url,
            headers={"User-Agent": "arch-mysetup"},
        )
        with urllib.request.urlopen(request, timeout=12) as response:
            content = response.read()
        if not content:
            return QUESTION_MARK_ICON_PATH
        icon_path.write_bytes(content)
        return icon_path
    except Exception:
        return QUESTION_MARK_ICON_PATH


def load_catalog_with_status(catalog_path: Path, icon_dir: Path):
    entries = []
    for entry in load_catalog_entries(catalog_path):
        entry_data = dict(entry)
        entry_data["installed"] = is_app_installed(entry["name"])
        entry_data["icon_path"] = str(ensure_catalog_icon(entry, icon_dir))
        entries.append(entry_data)
    return entries


def run_catalog_action(entry):
    method = get_install_method_from_source(entry.get("source"))
    if method is None:
        raise RuntimeError(f"Unknown install source for {entry['title']}")

    if entry.get("installed"):
        process = remove_apps(entry["name"], method)
    else:
        process = app_install(entry["name"], method)

    if not process:
        raise RuntimeError(f"Could not start package action for {entry['title']}")

    if hasattr(process, "wait"):
        process.wait()
