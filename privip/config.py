"""Configuración de usuario compartida por la GUI y el servicio."""
import json
import os

CONFIG_FILE = os.path.expanduser("~/.privip_config.json")
DEFAULT_CONFIG = {"interface": "wlan0", "auto_firefox": False}


def load_config(path=CONFIG_FILE):
    try:
        with open(path, "r") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return {**DEFAULT_CONFIG, **data}
    except (OSError, ValueError):
        pass
    return dict(DEFAULT_CONFIG)


def save_config(config, path=CONFIG_FILE):
    with open(path, "w") as f:
        json.dump(config, f)
