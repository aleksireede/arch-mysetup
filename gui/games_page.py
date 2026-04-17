from .catalog_page import CatalogPage
from programs.games_logic import load_games_with_status, run_game_action


class GamesPage(CatalogPage):
    def __init__(self, setup_window=None):
        super().__init__(setup_window, "Games", "Games", load_games_with_status, run_game_action)
