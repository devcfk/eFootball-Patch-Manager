import threading
from tkinter import messagebox
from typing import TYPE_CHECKING

import customtkinter as ctk

if TYPE_CHECKING:
    from .app import PatchManagerApp


class TabUninst:
    def __init__(self, parent: ctk.CTkFrame, app: "PatchManagerApp"):
        self._app = app
        self._backup_folder_win = ""

        f1 = ctk.CTkFrame(parent)
        f1.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(f1, text="Détails du patch actuel", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=10, pady=5
        )
        self.lbl_uninst_info = ctk.CTkLabel(f1, text="Aucun patch détecté.", justify="left")
        self.lbl_uninst_info.pack(anchor="w", padx=10, pady=5)

        row_backup = ctk.CTkFrame(f1, fg_color="transparent")
        row_backup.pack(fill="x", padx=10, pady=(0, 6))
        self.lbl_backup_path = ctk.CTkLabel(
            row_backup, text="", justify="left",
            font=ctk.CTkFont(size=11), text_color="gray60",
        )
        self.lbl_backup_path.pack(side="left", fill="x", expand=True)
        self.btn_copy_path = ctk.CTkButton(
            row_backup, text="📋", width=32, height=24,
            command=self._copy_backup_path,
        )
        self.btn_copy_path.pack(side="right", padx=(6, 0))
        self.btn_copy_path.pack_forget()

        self.chk_delete_backup_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            parent,
            text="Supprimer les backups après restauration",
            variable=self.chk_delete_backup_var,
        ).pack(anchor="w", padx=10, pady=(10, 2))

        self.btn_uninst = ctk.CTkButton(
            parent,
            text="DÉSINSTALLER ET RESTAURER",
            fg_color="#dc3545",
            hover_color="#c82333",
            command=self._start_uninstall,
        )
        self.btn_uninst.pack(anchor="w", padx=10, pady=(2, 10))

    def update(self, patch: dict | None) -> None:
        if patch:
            modules = patch.get("modules", [])
            mod_summary = (
                f"\nModules : {len(modules)} installé(s) — "
                + ", ".join(m["name"] for m in modules)
                if modules else "\nModules : aucun"
            )
            self.lbl_uninst_info.configure(
                text=(
                    f"Fichiers remplacés : {len(patch['replaced_files'])}\n"
                    f"Fichiers ajoutés : {len(patch['added_files'])}"
                    f"{mod_summary}"
                )
            )
            raw = patch.get("backup_folder", "")
            self._backup_folder_win = raw.replace("/", "\\")
            self.lbl_backup_path.configure(
                text=f"Dossier backup : {self._backup_folder_win}"
            )
            self.btn_copy_path.pack(side="right", padx=(6, 0))
            self.lbl_backup_path.pack(side="left", fill="x", expand=True)
            self.btn_uninst.configure(state="normal")
        else:
            self.lbl_uninst_info.configure(text="Aucun patch détecté.")
            self._backup_folder_win = ""
            self.lbl_backup_path.configure(text="")
            self.btn_copy_path.pack_forget()
            self.btn_uninst.configure(state="disabled")

    def _copy_backup_path(self) -> None:
        if self._backup_folder_win:
            self._app.clipboard_clear()
            self._app.clipboard_append(self._backup_folder_win)

    def _start_uninstall(self) -> None:
        if self._app.is_processing:
            return

        config_data = self._app.config_manager.load()
        patch = config_data.get("current_patch")
        if not patch:
            return

        # Vérification d'intégrité
        issues = self._app.install_service.verify_before_uninstall(patch)
        if issues:
            lines = []
            for layer_name, missing in issues.items():
                lines.append(f"{layer_name} :")
                for f in missing[:5]:
                    lines.append(f"  • {f}")
                if len(missing) > 5:
                    lines.append(f"  ... et {len(missing) - 5} autre(s)")
            warn_msg = (
                "Certains fichiers backup sont introuvables :\n\n"
                + "\n".join(lines)
                + "\n\nLes fichiers originaux correspondants ne pourront pas être restaurés.\n"
                "Continuer quand même ?"
            )
            if not messagebox.askyesno("Avertissement — backup incomplet", warn_msg, icon="warning"):
                return

        if messagebox.askyesno(
            "Confirmation",
            "Voulez-vous vraiment désinstaller le patch et restaurer les fichiers originaux ?",
        ):
            self._app.is_processing = True
            self.btn_uninst.configure(state="disabled")
            delete_backups = self.chk_delete_backup_var.get()
            threading.Thread(
                target=self._process_uninstall, args=(delete_backups,), daemon=True
            ).start()

    def _process_uninstall(self, delete_backups: bool) -> None:
        try:
            self._app.install_service.uninstall(silent=False, delete_backups=delete_backups)
            self._app.after(0, lambda: messagebox.showinfo("Succès", "Patch désinstallé et jeu restauré."))
        except Exception as e:
            msg = str(e)
            self._app.logger.log(f"Erreur de désinstallation : {msg}", "ERROR")
            self._app.set_progress(0.0, "Erreur.")
            self._app.after(0, lambda: messagebox.showerror("Erreur", "La désinstallation a échoué."))
        finally:
            self._app.is_processing = False
            self._app.after(0, self._app.update_ui)
