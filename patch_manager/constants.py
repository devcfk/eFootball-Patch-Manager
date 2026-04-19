import os

def _p(*parts: str) -> str:
    """Construit un chemin avec des séparateurs '/' (cohérence multi-contexte)."""
    return os.path.join(*parts).replace("\\", "/")


APPDATA_DIR = _p(os.environ.get("APPDATA", ""), "eFootball_PatchManager")
CONFIG_FILE = _p(APPDATA_DIR, "config.json")
LOG_FILE = _p(APPDATA_DIR, "patch_manager.log")

APPDATA_DIR_TEST = _p(os.environ.get("APPDATA", ""), "eFootball_PatchManager_Test")
CONFIG_FILE_TEST = _p(APPDATA_DIR_TEST, "config.json")
LOG_FILE_TEST = _p(APPDATA_DIR_TEST, "patch_manager.log")

# Rotation des logs
LOG_MAX_SIZE_MB   = 3    # Taille max avant rotation (Mo)
LOG_MAX_SESSIONS  = 10   # Nombre de sessions à conserver après rotation

DEFAULT_CONFIG = {
    "game_path": "",
    "backup_root": _p(APPDATA_DIR, "backups"),
    "sevenzip_path": "C:/Program Files/7-Zip/7z.exe",
    "current_patch": None,
    "history": [],
}
