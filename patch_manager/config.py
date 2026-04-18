import json
import os
from .constants import CONFIG_FILE, DEFAULT_CONFIG


class ConfigManager:
    def __init__(self, config_path: str = CONFIG_FILE):
        self._path = config_path

    def load(self) -> dict:
        cfg = {**DEFAULT_CONFIG, "backup_root": DEFAULT_CONFIG["backup_root"]}
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    cfg.update(json.load(f))
            except Exception:
                pass
        return cfg

    def save(self, data: dict) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
