import os
import shutil
import subprocess
import zipfile
from abc import ABC, abstractmethod
from typing import Generator, List, Tuple

import py7zr
import rarfile


class AbstractFileSystemOps(ABC):
    @abstractmethod
    def makedirs(self, path: str, exist_ok: bool = False) -> None: ...

    @abstractmethod
    def copy2(self, src: str, dst: str) -> None: ...

    @abstractmethod
    def remove(self, path: str) -> None: ...

    @abstractmethod
    def rmtree(self, path: str, ignore_errors: bool = False) -> None: ...

    @abstractmethod
    def exists(self, path: str) -> bool: ...

    @abstractmethod
    def walk(self, top: str) -> Generator[Tuple[str, List[str], List[str]], None, None]: ...

    @abstractmethod
    def extract(self, archive: str, dest: str, sevenzip_exe: str = "") -> None: ...


class RealFileSystemOps(AbstractFileSystemOps):
    def makedirs(self, path: str, exist_ok: bool = False) -> None:
        os.makedirs(path, exist_ok=exist_ok)

    def copy2(self, src: str, dst: str) -> None:
        shutil.copy2(src, dst)

    def remove(self, path: str) -> None:
        os.remove(path)

    def rmtree(self, path: str, ignore_errors: bool = False) -> None:
        shutil.rmtree(path, ignore_errors=ignore_errors)

    def exists(self, path: str) -> bool:
        return os.path.exists(path)

    def walk(self, top: str) -> Generator[Tuple[str, List[str], List[str]], None, None]:
        return os.walk(top)

    def extract(self, archive: str, dest: str, sevenzip_exe: str = "") -> None:
        ext = archive.lower()

        # 7-Zip externe en priorité si disponible (supporte tous les formats)
        if sevenzip_exe and os.path.exists(sevenzip_exe):
            subprocess.run(
                [sevenzip_exe, "x", archive, f"-o{dest}", "-y"],
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        elif ext.endswith(".zip"):
            with zipfile.ZipFile(archive, "r") as zf:
                zf.extractall(dest)
        elif ext.endswith(".7z"):
            with py7zr.SevenZipFile(archive, mode="r") as zf:
                zf.extractall(path=dest)
        elif ext.endswith(".rar"):
            with rarfile.RarFile(archive, "r") as rf:
                rf.extractall(path=dest)
        else:
            raise Exception(f"Format d'archive non supporté : {archive}")


class DryRunFileSystemOps(AbstractFileSystemOps):
    """Simule toutes les opérations FS sans modifier le disque.

    Utilise un faux arbre de fichiers pour simuler une extraction réaliste.
    Les opérations effectuées sont tracées dans operations_log.
    """

    FAKE_FILES = [
        "data/dt18_patch_001.pac",
        "data/dt18_patch_002.pac",
        "common/img/team_badge.png",
        "common/sound/crowd.acb",
        "content/native/x64/shader.pak",
    ]

    def __init__(self, game_path: str = "", archive_path: str = ""):
        self._game_path = game_path
        self._archive_path = archive_path
        self._virtual_fs: List[str] = []
        self.operations_log: List[dict] = []

    def _log_op(self, op: str, **kwargs) -> None:
        self.operations_log.append({"op": op, **kwargs})

    def makedirs(self, path: str, exist_ok: bool = False) -> None:
        self._log_op("makedirs", path=path, exist_ok=exist_ok)

    def copy2(self, src: str, dst: str) -> None:
        self._log_op("copy2", src=src, dst=dst)

    def remove(self, path: str) -> None:
        self._log_op("remove", path=path)

    def rmtree(self, path: str, ignore_errors: bool = False) -> None:
        self._log_op("rmtree", path=path, ignore_errors=ignore_errors)

    def exists(self, path: str) -> bool:
        if path == self._archive_path:
            return True
        if self._game_path and path.startswith(self._game_path):
            return True
        return os.path.exists(path)

    def walk(self, top: str) -> Generator[Tuple[str, List[str], List[str]], None, None]:
        dirs_seen: dict = {}
        for rel in self._virtual_fs:
            parts = rel.replace("\\", "/").split("/")
            dirname = os.path.join(top, *parts[:-1]) if len(parts) > 1 else top
            filename = parts[-1]
            dirs_seen.setdefault(dirname, []).append(filename)
        for dirpath, filenames in dirs_seen.items():
            yield dirpath, [], filenames

    def extract(self, archive: str, dest: str, sevenzip_exe: str = "") -> None:
        self._virtual_fs = list(self.FAKE_FILES)
        self._log_op("extract", archive=archive, files=self._virtual_fs)
