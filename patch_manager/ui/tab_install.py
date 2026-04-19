import threading
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING

import customtkinter as ctk

from ..installer import check_disk_space

if TYPE_CHECKING:
    from .app import PatchManagerApp


class TabInstall:
    def __init__(self, parent: ctk.CTkFrame, app: "PatchManagerApp"):
        self._app = app

        # Etape 1
        f1 = ctk.CTkFrame(parent)
        f1.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(f1, text="Étape 1 : Choisir l'équipe", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=10, pady=5
        )
        self.radio_var = ctk.StringVar(value="evomod")
        ctk.CTkRadioButton(f1, text="evomod", variable=self.radio_var, value="evomod").pack(
            side="left", padx=10, pady=10
        )
        ctk.CTkRadioButton(f1, text="ePatch", variable=self.radio_var, value="ePatch").pack(
            side="left", padx=10, pady=10
        )

        # Etape 2
        f2 = ctk.CTkFrame(parent)
        f2.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(
            f2,
            text="Étape 2 : Sélectionner l'archive (ZIP, RAR, 7Z)",
            font=ctk.CTkFont(weight="bold"),
        ).pack(anchor="w", padx=10, pady=5)
        row = ctk.CTkFrame(f2, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=5)
        self.txt_zip = ctk.CTkEntry(row)
        self.txt_zip.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(row, text="Parcourir...", width=100, command=self._browse_zip).pack(
            side="right"
        )

        # Etape 3
        f3 = ctk.CTkFrame(parent)
        f3.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(f3, text="Étape 3 : Installation", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=10, pady=5
        )
        self.btn_install = ctk.CTkButton(
            f3,
            text="INSTALLER LE PATCH",
            fg_color="#28a745",
            hover_color="#218838",
            command=self._start_install,
        )
        self.btn_install.pack(anchor="w", padx=10, pady=10)

    def _browse_zip(self) -> None:
        file = filedialog.askopenfilename(filetypes=[("Archives", "*.zip *.rar *.7z")])
        if file:
            self.txt_zip.delete(0, "end")
            self.txt_zip.insert(0, file)

    def _start_install(self) -> None:
        if self._app.is_processing:
            return

        config_data = self._app.config_manager.load()
        game_path = config_data.get("game_path", "")
        zip_path = self.txt_zip.get()

        if not game_path or not self._app.fs_ops.exists(game_path):
            messagebox.showerror("Erreur", "Le dossier du jeu n'est pas configuré.")
            return
        if not zip_path or not self._app.fs_ops.exists(zip_path):
            messagebox.showerror("Erreur", "Archive introuvable.")
            return
        if config_data.get("current_patch"):
            if not messagebox.askyesno(
                "Attention", "Un patch est déjà installé. Désinstaller avant de continuer ?"
            ):
                return
            self._run_uninstall(silent=True)

        ok, needed, free = check_disk_space(zip_path, game_path)
        if not ok:
            if not messagebox.askyesno(
                "Espace disque insuffisant",
                f"Espace estimé nécessaire : {needed:.0f} Mo\n"
                f"Espace disponible : {free:.0f} Mo\n\n"
                "L'installation pourrait échouer faute d'espace.\n"
                "Continuer quand même ?",
                icon="warning",
            ):
                return

        self._app.is_processing = True
        self.btn_install.configure(state="disabled")
        threading.Thread(
            target=self._process_install,
            args=(self.radio_var.get(), zip_path),
            daemon=True,
        ).start()

    def _run_uninstall(self, silent: bool = True) -> None:
        try:
            self._app.install_service.uninstall(silent=silent)
        except Exception as e:
            self._app.logger.log(f"Erreur désinstallation silencieuse : {e}", "ERROR")
        finally:
            self._app.after(0, self._app.update_ui)

    def _process_install(self, team: str, zip_path: str) -> None:
        try:
            self._app.install_service.install(team, zip_path)
            self._app.after(0, lambda: messagebox.showinfo("Succès", "Patch installé avec succès."))
        except Exception as e:
            msg = str(e)
            self._app.logger.log(f"Erreur d'installation : {msg}", "ERROR")
            self._app.set_progress(0.0, "Erreur.")
            self._app.after(
                0, lambda m=msg: messagebox.showerror("Erreur", f"L'installation a échoué.\n{m}")
            )
        finally:
            self._app.is_processing = False
            self._app.after(0, lambda: self.btn_install.configure(state="normal"))
            self._app.after(0, self._app.update_ui)
