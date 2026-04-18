import os
import subprocess
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING

import customtkinter as ctk

if TYPE_CHECKING:
    from .app import PatchManagerApp

SEVENZIP_URL = "https://www.7-zip.org/download.html"


def _normalize(path: str) -> str:
    """Normalise les séparateurs vers '/' pour un affichage cohérent."""
    return path.replace("\\", "/") if path else path


class TabParam:
    def __init__(self, parent: ctk.CTkFrame, app: "PatchManagerApp"):
        self._app = app

        f = ctk.CTkFrame(parent)
        f.pack(fill="x", padx=10, pady=10)

        self.txt_game_path = self._create_path_entry(f, "Dossier du jeu eFootball", self._browse_folder)
        self.txt_backup_path = self._create_path_entry(f, "Dossier de sauvegarde (Backups)", self._browse_folder)
        self.txt_7z_path = self._create_path_entry(f, "Chemin vers 7z.exe  (optionnel)", self._browse_7z)

        # Lien téléchargement 7-Zip
        lbl_7z_link = ctk.CTkLabel(
            f,
            text="Télécharger 7-Zip : " + SEVENZIP_URL,
            text_color=("blue", "#5b9bd5"),
            cursor="hand2",
            font=ctk.CTkFont(size=12),
        )
        lbl_7z_link.pack(anchor="w", padx=10, pady=(0, 8))
        lbl_7z_link.bind("<Button-1>", lambda _: subprocess.Popen(["start", SEVENZIP_URL], shell=True))

        ctk.CTkButton(parent, text="SAUVEGARDER", command=self._save_settings).pack(
            anchor="w", padx=10, pady=20
        )

    def _create_path_entry(self, parent, label_text: str, browse_command) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=10, pady=(10, 0)
        )
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=5)
        entry = ctk.CTkEntry(row)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(row, text="Parcourir...", width=100, command=lambda: browse_command(entry)).pack(
            side="right"
        )
        return entry

    def _browse_folder(self, entry: ctk.CTkEntry) -> None:
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, "end")
            entry.insert(0, _normalize(folder))

    def _browse_7z(self, entry: ctk.CTkEntry) -> None:
        file = filedialog.askopenfilename(filetypes=[("Exécutable", "7z.exe")])
        if file:
            entry.delete(0, "end")
            entry.insert(0, _normalize(file))

    def _save_settings(self) -> None:
        config_data = self._app.config_manager.load()
        config_data["game_path"] = _normalize(self.txt_game_path.get())
        config_data["backup_root"] = _normalize(self.txt_backup_path.get())
        config_data["sevenzip_path"] = _normalize(self.txt_7z_path.get())
        self._app.config_manager.save(config_data)
        self._app.logger.log("Paramètres sauvegardés.", "OK")
        messagebox.showinfo("Succès", "Paramètres enregistrés.")

    def load_values(self, config_data: dict) -> None:
        self.txt_game_path.delete(0, "end")
        self.txt_game_path.insert(0, _normalize(config_data.get("game_path", "")))
        self.txt_backup_path.delete(0, "end")
        self.txt_backup_path.insert(0, _normalize(config_data.get("backup_root", "")))
        self.txt_7z_path.delete(0, "end")
        self.txt_7z_path.insert(0, _normalize(config_data.get("sevenzip_path", "")))
