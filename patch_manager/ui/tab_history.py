import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import PatchManagerApp


class TabHistory:
    def __init__(self, parent: ctk.CTkFrame, app: "PatchManagerApp"):
        self._app = app

        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 4))
        ctk.CTkLabel(
            header, text="Historique des patches désinstallés",
            font=ctk.CTkFont(weight="bold", size=14),
        ).pack(side="left")
        self._lbl_count = ctk.CTkLabel(header, text="", text_color="gray60",
                                        font=ctk.CTkFont(size=12))
        self._lbl_count.pack(side="left", padx=10)

        self._scroll = ctk.CTkScrollableFrame(parent)
        self._scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._empty_label = ctk.CTkLabel(
            self._scroll, text="Aucun historique disponible.",
            text_color="gray60",
        )
        self._empty_label.pack(anchor="w", padx=10, pady=10)

    def update(self, history: list) -> None:
        for w in self._scroll.winfo_children():
            w.destroy()

        if not history:
            ctk.CTkLabel(
                self._scroll, text="Aucun historique disponible.",
                text_color="gray60",
            ).pack(anchor="w", padx=10, pady=10)
            self._lbl_count.configure(text="")
            return

        self._lbl_count.configure(text=f"({len(history)} entrée(s))")

        # Plus récent en premier
        for entry in reversed(history):
            self._build_entry(entry)

    def _build_entry(self, entry: dict) -> None:
        card = ctk.CTkFrame(self._scroll, corner_radius=8,
                             fg_color=("gray88", "gray17"))
        card.pack(fill="x", padx=4, pady=5)

        # --- Ligne titre ---
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(8, 2))

        team = entry.get("team", "—").upper()
        ctk.CTkLabel(
            top, text=team,
            font=ctk.CTkFont(weight="bold", size=13),
        ).pack(side="left")

        uninstall_date = entry.get("uninstall_date", "")[:10]
        ctk.CTkLabel(
            top, text=f"Désinstallé le {uninstall_date}",
            text_color="gray60", font=ctk.CTkFont(size=11),
        ).pack(side="right")

        # --- Détails ---
        install_date = entry.get("install_date", "")[:10]
        file_count   = entry.get("file_count", 0)
        replaced     = len(entry.get("replaced_files", []))
        added        = len(entry.get("added_files", []))
        modules      = entry.get("modules", [])

        details = (
            f"Installé le : {install_date}   |   "
            f"{file_count} fichiers   |   "
            f"{replaced} remplacé(s)  {added} ajouté(s)"
        )
        ctk.CTkLabel(
            card, text=details,
            text_color="gray60", font=ctk.CTkFont(size=11), justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 2))

        # --- Modules ---
        if modules:
            mod_text = "Modules : " + ",  ".join(m["name"] for m in modules)
            ctk.CTkLabel(
                card, text=mod_text,
                text_color="gray50", font=ctk.CTkFont(size=11), justify="left",
            ).pack(anchor="w", padx=12, pady=(0, 4))

        # --- Chemin backup ---
        backup = entry.get("backup_folder", "").replace("/", "\\")
        if backup:
            row_bkp = ctk.CTkFrame(card, fg_color="transparent")
            row_bkp.pack(fill="x", padx=12, pady=(0, 8))
            ctk.CTkLabel(
                row_bkp,
                text=f"Backup : {backup}",
                text_color="gray50", font=ctk.CTkFont(size=10), justify="left",
            ).pack(side="left", fill="x", expand=True)
            ctk.CTkButton(
                row_bkp, text="📋", width=28, height=20,
                command=lambda p=backup: self._copy(p),
            ).pack(side="right", padx=(6, 0))

    def _copy(self, path: str) -> None:
        self._app.clipboard_clear()
        self._app.clipboard_append(path)
