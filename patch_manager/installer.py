import datetime
import os
from typing import Callable

from .config import ConfigManager
from .fs_ops import AbstractFileSystemOps
from .logger import Logger


def _stem(path: str) -> str:
    """Déduit un nom lisible depuis le nom de fichier de l'archive."""
    base = os.path.basename(path)
    name, _ = os.path.splitext(base)
    return name.replace("_", " ").replace("-", " ")


def _safe_folder_name(name: str) -> str:
    """Sanitize un nom pour l'utiliser dans un chemin de dossier Windows."""
    invalid = r'\/:*?"<>|'
    sanitized = "".join("_" if c in invalid else c for c in name)
    return sanitized.strip(". ")[:40]


def _copy_tree(fs: AbstractFileSystemOps, all_files: list, dest_root: str,
               backup_dir: str, existing_backups: set,
               replaced: list, added: list, progress_cb: Callable,
               logger: Logger, progress_start: float = 0.2) -> None:
    """Copie les fichiers vers dest_root avec backup, en évitant de re-sauvegarder
    un fichier déjà sauvegardé par un module précédent (préserve l'original)."""
    file_count = len(all_files)
    for i, (src_file, rel_path) in enumerate(all_files):
        dest_file = os.path.join(dest_root, rel_path).replace("\\", "/")
        backup_file = os.path.join(backup_dir, rel_path).replace("\\", "/")

        fs.makedirs(os.path.dirname(dest_file), exist_ok=True)

        if fs.exists(dest_file):
            if rel_path not in existing_backups:
                fs.makedirs(os.path.dirname(backup_file), exist_ok=True)
                fs.copy2(dest_file, backup_file)
                logger.log(f"  [REMPLACÉ]  {dest_file}  →  backup : {backup_file}", "INFO")
            else:
                logger.log(f"  [REMPLACÉ]  {dest_file}  (backup existant conservé)", "INFO")
            replaced.append(rel_path)
        else:
            logger.log(f"  [AJOUTÉ]    {dest_file}", "INFO")
            added.append(rel_path)

        fs.copy2(src_file, dest_file)

        if i % 50 == 0:
            prog = progress_start + (i / file_count) * (0.95 - progress_start)
            progress_cb(prog, f"Copie des fichiers ({i}/{file_count})...")


class InstallService:
    def __init__(
        self,
        config_manager: ConfigManager,
        fs_ops: AbstractFileSystemOps,
        logger: Logger,
        progress_callback: Callable[[float, str], None],
        appdata_dir: str = "",
    ):
        self._cfg = config_manager
        self._fs = fs_ops
        self._log = logger
        self._progress = progress_callback
        self._appdata_dir = appdata_dir

    # ------------------------------------------------------------------
    # Utilitaire extraction
    # ------------------------------------------------------------------
    def _extract_to_temp(self, zip_path: str, config_data: dict) -> tuple[str, list]:
        """Extrait une archive dans un dossier temp et retourne (temp_dir, all_files)."""
        temp_dir = os.path.join(self._appdata_dir, "temp_extract")
        if self._fs.exists(temp_dir):
            self._fs.rmtree(temp_dir)
        self._fs.makedirs(temp_dir, exist_ok=True)

        exe_7z = config_data.get("sevenzip_path", "")
        self._fs.extract(zip_path, temp_dir, sevenzip_exe=exe_7z)

        all_files = []
        for root, _dirs, files in self._fs.walk(temp_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, temp_dir)
                all_files.append((full_path, rel_path))

        if not all_files:
            raise Exception("Archive vide.")
        return temp_dir, all_files

    def _existing_backup_files(self, config_data: dict) -> set:
        """Retourne l'ensemble des rel_path déjà sauvegardés (patch + modules)."""
        backed_up = set()
        patch = config_data.get("current_patch")
        if not patch:
            return backed_up
        backed_up.update(patch.get("replaced_files", []))
        for mod in patch.get("modules", []):
            backed_up.update(mod.get("replaced_files", []))
        return backed_up

    # ------------------------------------------------------------------
    # Installation du patch principal
    # ------------------------------------------------------------------
    def install(self, team: str, zip_path: str) -> None:
        config_data = self._cfg.load()
        temp_dir = ""
        try:
            self._log.log_separator(f"Installation patch — {team}")
            self._log.log(f"Début de l'installation de {team}")
            self._progress(0.05, "Extraction de l'archive...")

            temp_dir, all_files = self._extract_to_temp(zip_path, config_data)
            file_count = len(all_files)

            self._progress(0.2, "Création des sauvegardes et copie...")
            date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
            backup_dir = os.path.join(config_data["backup_root"], f"{team}_{date_str}")

            replaced, added = [], []
            _copy_tree(self._fs, all_files, config_data["game_path"],
                       backup_dir, set(), replaced, added, self._progress, self._log)

            self._progress(0.95, "Sauvegarde de la configuration...")
            config_data["current_patch"] = {
                "team": team,
                "install_date": datetime.datetime.now().isoformat(),
                "backup_folder": backup_dir,
                "source_zip": zip_path,
                "file_count": file_count,
                "replaced_files": replaced,
                "added_files": added,
                "modules": [],
            }
            self._cfg.save(config_data)

            self._log.log(f"Installation terminée avec succès ({file_count} fichiers).", "OK")
            self._progress(1.0, "Terminé.")

        finally:
            if temp_dir and self._fs.exists(temp_dir):
                self._fs.rmtree(temp_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # Installation d'un module additionnel
    # ------------------------------------------------------------------
    def install_module(self, zip_path: str, install_path: str = "") -> None:
        config_data = self._cfg.load()
        patch = config_data.get("current_patch")
        if not patch:
            raise Exception("Aucun patch de base installé. Installez d'abord un patch principal.")

        temp_dir = ""
        try:
            name = _stem(zip_path)
            self._log.log_separator(f"Installation module — {name}")
            self._log.log(f"Début de l'installation du module « {name} »")
            self._progress(0.05, "Extraction de l'archive...")

            temp_dir, all_files = self._extract_to_temp(zip_path, config_data)
            file_count = len(all_files)

            self._progress(0.2, "Création des sauvegardes et copie...")
            date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
            module_index = len(patch.get("modules", []))
            safe_name = _safe_folder_name(name)
            backup_dir = os.path.join(
                patch["backup_folder"], f"module_{module_index}_{safe_name}_{date_str}"
            )

            # Destination : game_path par défaut, ou chemin personnalisé
            dest_root = install_path if install_path else config_data["game_path"]

            existing_backups = self._existing_backup_files(config_data)
            replaced, added = [], []
            _copy_tree(self._fs, all_files, dest_root,
                       backup_dir, existing_backups, replaced, added, self._progress, self._log)

            self._progress(0.95, "Sauvegarde de la configuration...")
            patch.setdefault("modules", []).append({
                "name": name,
                "install_date": datetime.datetime.now().isoformat(),
                "install_order": module_index,
                "source_zip": zip_path,
                "install_path": dest_root,
                "backup_folder": backup_dir,
                "file_count": file_count,
                "replaced_files": replaced,
                "added_files": added,
            })
            self._cfg.save(config_data)

            self._log.log(f"Module « {name} » installé ({file_count} fichiers).", "OK")
            self._progress(1.0, "Terminé.")

        finally:
            if temp_dir and self._fs.exists(temp_dir):
                self._fs.rmtree(temp_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # Désinstallation d'un module seul
    # ------------------------------------------------------------------
    def uninstall_module(self, module_index: int, delete_backup: bool = False) -> None:
        config_data = self._cfg.load()
        patch = config_data.get("current_patch")
        if not patch:
            raise Exception("Aucun patch de base installé.")

        modules = patch.get("modules", [])
        if module_index < 0 or module_index >= len(modules):
            raise Exception(f"Module introuvable (index {module_index}).")

        mod = modules[module_index]
        game_path = config_data.get("game_path", "")
        dest_root = mod.get("install_path", game_path)

        self._log.log_separator(f"Désinstallation module — {mod['name']}")
        self._log.log(f"Suppression du module « {mod['name']} »...")
        self._progress(0.1, f"Suppression module : {mod['name']}...")

        self._remove_layer(mod, dest_root)
        self._progress(0.9, "Sauvegarde de la configuration...")

        if delete_backup:
            self._delete_backup_folder(mod["backup_folder"])

        patch["modules"].pop(module_index)
        # Réindexe les install_order restants
        for i, m in enumerate(patch["modules"]):
            m["install_order"] = i

        self._cfg.save(config_data)
        self._progress(1.0, "Terminé.")
        self._log.log(f"Module « {mod['name']} » désinstallé.", "OK")

    # ------------------------------------------------------------------
    # Désinstallation (patch + tous les modules, ordre inverse)
    # ------------------------------------------------------------------
    def uninstall(self, silent: bool = False, delete_backups: bool = False) -> None:
        config_data = self._cfg.load()
        patch = config_data.get("current_patch")
        if not patch:
            return

        game_path = config_data.get("game_path", "")
        modules = list(patch.get("modules", []))
        self._log.log_separator(f"Désinstallation patch — {patch['team']}")

        total_steps = len(modules) + 1
        step = 0

        # Désinstalle les modules en ordre inverse
        for mod in reversed(modules):
            step += 1
            self._log.log(f"Suppression du module « {mod['name']} »...")
            self._progress(step / total_steps * 0.9, f"Suppression module : {mod['name']}...")
            dest_root = mod.get("install_path", game_path)
            self._remove_layer(mod, dest_root)
            if delete_backups:
                self._delete_backup_folder(mod["backup_folder"])

        # Désinstalle le patch principal
        step += 1
        self._log.log(f"Désinstallation du patch {patch['team']}...")
        self._progress(step / total_steps * 0.9, "Restauration du patch principal...")
        self._remove_layer(patch, game_path)
        if delete_backups:
            self._delete_backup_folder(patch["backup_folder"])

        patch["uninstall_date"] = datetime.datetime.now().isoformat()
        config_data["history"].append(patch)
        config_data["current_patch"] = None
        self._cfg.save(config_data)

        self._progress(1.0, "Désinstallation terminée.")
        self._log.log("Désinstallation terminée avec succès.", "OK")

    def _delete_backup_folder(self, backup_folder: str) -> None:
        if self._fs.exists(backup_folder):
            self._fs.rmtree(backup_folder, ignore_errors=True)
            self._log.log(f"  [BACKUP SUPPRIMÉ]  {backup_folder}", "INFO")

    def _remove_layer(self, layer: dict, dest_root: str) -> None:
        """Supprime les fichiers ajoutés et restaure les backups d'une couche (patch ou module)."""
        backup_path = layer["backup_folder"]

        for rel in layer.get("added_files", []):
            target = os.path.join(dest_root, rel).replace("\\", "/")
            if self._fs.exists(target):
                self._fs.remove(target)
                self._log.log(f"  [SUPPRIMÉ]  {target}", "INFO")

        for rel in layer.get("replaced_files", []):
            target = os.path.join(dest_root, rel).replace("\\", "/")
            bkp = os.path.join(backup_path, rel).replace("\\", "/")
            if self._fs.exists(bkp):
                self._fs.copy2(bkp, target)
                self._log.log(f"  [RESTAURÉ]  {bkp}  →  {target}", "INFO")
