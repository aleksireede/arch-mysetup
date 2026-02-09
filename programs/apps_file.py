from pathlib import Path
import sys
import yaml

parent_dir = str(Path(__file__).resolve().parent.parent.joinpath("programs"))
sys.path.append(parent_dir)

from installer_logic import detect_install_method

yaml_path = Path(__file__).parent.parent.resolve().joinpath("apps.yaml")


def load_apps_from_file():
    return get_apps(load_yaml())


def load_yaml():
    if not yaml_path.exists():
        return []

    with open(yaml_path, "r") as f:
        try:
            data = yaml.safe_load(f)
            if not isinstance(data, list):
                return []
            return data
        except yaml.YAMLError:
            return []


def get_apps(yaml_data):
    """Extract apps from YAML data into a list."""
    return [app['name'] for app in yaml_data if 'name' in app]


def add_app_to_yaml(app):
    yaml_data = load_yaml()
    source = detect_install_method(app)
    application = {
        "name": app,
        "description": f"Default description for {app}",
        "source": source if source else "Unknown",
        "category": "Utilities",
        "conflicts": []
    }
    yaml_data.append(application)
    write_to_yaml(yaml_data)


def remove_app_from_yaml(app):
    yaml_data = load_yaml()
    yaml_data.remove(app)
    write_to_yaml(yaml_data)


def write_to_yaml(yaml_data):
    yaml_data.sort(key=lambda x: x["name"])
    with open(yaml_path, "w") as f:
        yaml.safe_dump(yaml_data, f, sort_keys=False)
