import datetime
import os
from typing import Callable, Optional


class Logger:
    def __init__(self, log_file: str, ui_callback: Optional[Callable[[str], None]] = None):
        self._log_file = log_file
        self._ui_callback = ui_callback

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
