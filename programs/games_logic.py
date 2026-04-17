import re
import urllib.request
from pathlib import Path

import yaml

from programs.config import GAME_CATALOG_PATH, GAME_ICONS_DIR, QUESTION_MARK_ICON_PATH
from programs.installer_logic import (
    app_install,
    get_install_method_from_source,
    is_app_installed,
    remove_apps,
)


def load_games():
    if not GAME_CATALOG_PATH.exists():
        return []

    with open(GAME_CATALOG_PATH, "r", encoding="utf-8") as game_file:
        data = yaml.safe_load(game_file) or []

    games = []
    for game in data:
        if not isinstance(game, dict) or not game.get("name"):
            continue
        games.append(
            {
                "name": game["name"],
                "title": game.get("title", game["name"]),
                "description": game.get("description", ""),
                "source": game.get("source"),
                "icon_url": game.get("icon_url"),
            }
        )
    return games


def get_game_icon_path(game):
    GAME_ICONS_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", game["name"].lower()).strip("-")
    return GAME_ICONS_DIR.joinpath(f"{slug}.png")


def ensure_game_icon(game):
    icon_path = get_game_icon_path(game)
    if icon_path.exists():
        return icon_path

    icon_url = game.get("icon_url")
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


def load_games_with_status():
    games = []
    for game in load_games():
        game_data = dict(game)
        game_data["installed"] = is_app_installed(game["name"])
        game_data["icon_path"] = str(ensure_game_icon(game))
        games.append(game_data)
    return games


def run_game_action(game):
    method = get_install_method_from_source(game.get("source"))
    if method is None:
        raise RuntimeError(f"Unknown install source for {game['title']}")

    if game.get("installed"):
        process = remove_apps(game["name"], method)
    else:
        process = app_install(game["name"], method)

    if not process:
        raise RuntimeError(f"Could not start package action for {game['title']}")

    if hasattr(process, "wait"):
        process.wait()
