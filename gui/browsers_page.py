from .catalog_page import CatalogPage
from programs.browsers_logic import load_browsers_with_status, run_browser_action


class BrowsersPage(CatalogPage):
    def __init__(self, setup_window=None):
        super().__init__(
            setup_window,
            "Web Browsers",
            "Web Browsers",
            load_browsers_with_status,
            run_browser_action,
        )
