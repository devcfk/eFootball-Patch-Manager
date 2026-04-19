import datetime
import os
from typing import Callable, Optional

from .constants import LOG_MAX_SESSIONS, LOG_MAX_SIZE_MB


class Logger:
    def __init__(self, log_file: str, ui_callback: Optional[Callable[[str], None]] = None):
        self._log_file = log_file
        self._ui_callback = ui_callback
        self._rotate_if_needed()

    def set_ui_callback(self, callback: Callable[[str], None]) -> None:
        self._ui_callback = callback

    def log(self, message: str, level: str = "INFO") -> None:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{date_str}][{level}] {message}\n"
        os.makedirs(os.path.dirname(self._log_file), exist_ok=True)
        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(line)
        if self._ui_callback:
            self._ui_callback(line)

    def log_separator(self, title: str) -> None:
        date_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        bar = "═" * 60
        line = f"\n{bar}\n  {title}  —  {date_str}\n{bar}\n"
        os.makedirs(os.path.dirname(self._log_file), exist_ok=True)
        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(line)
        if self._ui_callback:
            self._ui_callback(line)

    # ------------------------------------------------------------------
    # Rotation
    # ------------------------------------------------------------------
    def _rotate_if_needed(self) -> None:
        if not os.path.exists(self._log_file):
            return
        size_mb = os.path.getsize(self._log_file) / (1024 * 1024)
        if size_mb < LOG_MAX_SIZE_MB:
            return

        with open(self._log_file, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Découpe sur les séparateurs de session (ligne de ═)
        sessions = self._split_sessions(content)

        # Archive le contenu actuel dans .log.bak (écrasé à chaque rotation)
        bak_file = self._log_file + ".bak"
        with open(bak_file, "w", encoding="utf-8") as f:
            f.write(content)

        # Conserve uniquement les N dernières sessions
        kept = sessions[-LOG_MAX_SESSIONS:] if len(sessions) > LOG_MAX_SESSIONS else sessions
        new_content = "".join(kept)

        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = (
            f"[{date_str}][INFO] --- Rotation du journal : "
            f"{len(sessions)} session(s) archivées dans {os.path.basename(bak_file)}, "
            f"{len(kept)} conservée(s). ---\n"
        )
        with open(self._log_file, "w", encoding="utf-8") as f:
            f.write(header + new_content)

    @staticmethod
    def _split_sessions(content: str) -> list[str]:
        """Découpe le contenu en blocs de sessions délimités par les lignes ═."""
        lines = content.splitlines(keepends=True)
        sessions: list[str] = []
        current: list[str] = []

        for line in lines:
            # Début d'un nouveau bloc séparateur = début d'une nouvelle session
            if line.strip() and all(c == "═" for c in line.strip()):
                if current:
                    sessions.append("".join(current))
                current = [line]
            else:
                current.append(line)

        if current:
            sessions.append("".join(current))

        # Si aucun séparateur trouvé (vieux log sans sessions), traiter comme 1 session
        return sessions if sessions else [content]
