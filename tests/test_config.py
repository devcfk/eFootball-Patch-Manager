import json
import os
import tempfile

from patch_manager.config import ConfigManager
from patch_manager.constants import DEFAULT_CONFIG


def test_load_returns_defaults_when_no_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = ConfigManager(os.path.join(tmpdir, "config.json"))
        data = cfg.load()
        assert data["game_path"] == DEFAULT_CONFIG["game_path"]
        assert data["current_patch"] is None
        assert isinstance(data["history"], list)


def test_save_and_reload():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "config.json")
        cfg = ConfigManager(path)
        original = cfg.load()
        original["game_path"] = "C:/Games/eFootball"
        cfg.save(original)

        reloaded = cfg.load()
        assert reloaded["game_path"] == "C:/Games/eFootball"


def test_load_merges_with_defaults():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "config.json")
        with open(path, "w") as f:
            json.dump({"game_path": "C:/custom"}, f)

        cfg = ConfigManager(path)
        data = cfg.load()
        assert data["game_path"] == "C:/custom"
        assert "sevenzip_path" in data
