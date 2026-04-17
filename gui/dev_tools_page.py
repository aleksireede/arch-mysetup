from .catalog_page import CatalogPage
from programs.dev_tools_logic import load_dev_tools_with_status, run_dev_tool_action


class DevToolsPage(CatalogPage):
    def __init__(self, setup_window=None):
        super().__init__(
            setup_window,
            "Developer Tools",
            "Developer Tools",
            load_dev_tools_with_status,
            run_dev_tool_action,
        )
