import threading
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING

import customtkinter as ctk

if TYPE_CHECKING:
    from .app import PatchManagerApp


class TabModules:
    def __init__(self, parent: ctk.CTkFrame, app: "PatchManagerApp"):
        self._app = app

        # --- Sélection de l'archive ---
        f_archive = ctk.CTkFrame(parent)
        f_archive.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(
            f_archive,
            text="Archive du module (ZIP, RAR, 7Z)",
            font=ctk.CTkFont(weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 0))
        row_archive = ctk.CTkFrame(f_archive, fg_color="transparent")
        row_archive.pack(fill="x", padx=10, pady=5)
        self.txt_archive = ctk.CTkEntry(row_archive, placeholder_text="Chemin vers l'archive...")
        self.txt_archive.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(
            row_archive, text="Parcourir...", width=100, command=self._browse_archive
        ).pack(side="right")

        # --- Chemin d'installation ---
        f_path = ctk.CTkFrame(parent)
        f_path.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(
            f_path,
            text="Dossier d'installation",
            font=ctk.CTkFont(weight="bold"),
        ).pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkLabel(
            f_path,
            text="Par défaut : dossier du jeu eFootball. Modifiable si le module s'installe ailleurs.",
            text_color="gray60",
            font=ctk.CTkFont(size=11),
        ).pack(anchor="w", padx=10)
        row_path = ctk.CTkFrame(f_path, fg_color="transparent")
        row_path.pack(fill="x", padx=10, pady=5)
        self.txt_install_path = ctk.CTkEntry(row_path, placeholder_text="Dossier du jeu (par défaut)")
        self.txt_install_path.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(
            row_path, text="Parcourir...", width=100, command=self._browse_install_path
        ).pack(side="right")

        # --- Bouton installer ---
        self.btn_install_module = ctk.CTkButton(
            parent,
            text="INSTALLER LE MODULE",
            fg_color="#17a2b8",
            hover_color="#138496",
            command=self._start_install_module,
        )
        self.btn_install_module.pack(anchor="w", padx=10, pady=15)

        # --- Liste des modules installés ---
        f_list = ctk.CTkFrame(parent)
        f_list.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        ctk.CTkLabel(
            f_list,
            text="Modules installés",
            font=ctk.CTkFont(weight="bold", size=13),
        ).pack(anchor="w", padx=10, pady=(8, 4))
        self._modules_frame = ctk.CTkScrollableFrame(f_list, height=180)
        self._modules_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self._no_module_label = ctk.CTkLabel(
            self._modules_frame, text="Aucun module installé.", text_color="gray60"
        )
        self._no_module_label.pack(anchor="w", padx=10, pady=5)

    # ------------------------------------------------------------------

    def _browse_archive(self) -> None:
        file = filedialog.askopenfilename(filetypes=[("Archives", "*.zip *.rar *.7z")])
        if file:
            self.txt_archive.delete(0, "end")
            self.txt_archive.insert(0, file.replace("\\", "/"))

    def _browse_install_path(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.txt_install_path.delete(0, "end")
            self.txt_install_path.insert(0, folder.replace("\\", "/"))

    def _start_install_module(self) -> None:
        if self._app.is_processing:
            return

        config_data = self._app.config_manager.load()
        if not config_data.get("current_patch"):
            messagebox.showerror(
                "Erreur", "Aucun patch de base installé.\nInstallez d'abord un patch principal."
            )
            return

        archive = self.txt_archive.get().strip()
        if not archive or not self._app.fs_ops.exists(archive):
            messagebox.showerror("Erreur", "Archive introuvable.")
            return

        # Chemin d'installation : champ si renseigné, sinon game_path
        install_path = self.txt_install_path.get().strip()
        if not install_path:
            install_path = config_data.get("game_path", "")

        self._app.is_processing = True
        self.btn_install_module.configure(state="disabled")
        threading.Thread(
            target=self._process_install_module,
            args=(archive, install_path),
            daemon=True,
        ).start()

    def _process_install_module(self, archive: str, install_path: str) -> None:
        try:
            self._app.install_service.install_module(archive, install_path)
            self._app.after(
                0, lambda: messagebox.showinfo("Succès", "Module installé avec succès.")
            )
        except Exception as e:
            msg = str(e)
            self._app.logger.log(f"Erreur installation module : {msg}", "ERROR")
            self._app.set_progress(0.0, "Erreur.")
            self._app.after(
                0, lambda m=msg: messagebox.showerror("Erreur", f"L'installation a échoué.\n{m}")
            )
        finally:
            self._app.is_processing = False
            self._app.after(0, lambda: self.btn_install_module.configure(state="normal"))
            self._app.after(0, self._app.update_ui)

    def update(self, patch: dict | None) -> None:
        """Rafraîchit la liste des modules et l'état du bouton."""
        # Active le bouton seulement si un patch de base est présent
        self.btn_install_module.configure(state="normal" if patch else "disabled")

        # Vide le scrollable frame
        for widget in self._modules_frame.winfo_children():
            widget.destroy()

        modules = patch.get("modules", []) if patch else []
        if not modules:
            ctk.CTkLabel(
                self._modules_frame, text="Aucun module installé.", text_color="gray60"
            ).pack(anchor="w", padx=10, pady=5)
            return

        for mod in modules:
            row = ctk.CTkFrame(self._modules_frame, fg_color=("gray85", "gray20"), corner_radius=6)
            row.pack(fill="x", padx=5, pady=4)
            ctk.CTkLabel(
                row,
                text=f"📦  {mod['name']}",
                font=ctk.CTkFont(weight="bold"),
            ).pack(anchor="w", padx=10, pady=(6, 2))
            ctk.CTkLabel(
                row,
                text=(
                    f"Installé le : {mod['install_date'][:10]}   |   "
                    f"{mod['file_count']} fichiers   |   "
                    f"Dossier : {mod['install_path']}"
                ),
                text_color="gray60",
                font=ctk.CTkFont(size=11),
            ).pack(anchor="w", padx=10, pady=(0, 6))
