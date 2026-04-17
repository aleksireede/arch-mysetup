from programs.catalog_logic import load_catalog_with_status, run_catalog_action
from programs.config import DEV_TOOL_CATALOG_PATH, DEV_TOOL_ICONS_DIR


def load_dev_tools_with_status():
    return load_catalog_with_status(DEV_TOOL_CATALOG_PATH, DEV_TOOL_ICONS_DIR)


def run_dev_tool_action(dev_tool):
    run_catalog_action(dev_tool)
