import customtkinter as ctk


class TabAccueil:
    def __init__(self, parent: ctk.CTkFrame):
        frame_status = ctk.CTkFrame(parent)
        frame_status.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(
            frame_status,
            text="Statut actuel",
            font=ctk.CTkFont(weight="bold", size=14),
        ).pack(anchor="w", padx=10, pady=5)
        self.lbl_status_info = ctk.CTkLabel(frame_status, text="Chargement...", justify="left")
        self.lbl_status_info.pack(anchor="w", padx=10, pady=5)

        frame_modules = ctk.CTkFrame(parent)
        frame_modules.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(
            frame_modules,
            text="Modules installés",
            font=ctk.CTkFont(weight="bold", size=14),
        ).pack(anchor="w", padx=10, pady=5)
        self.lbl_modules_info = ctk.CTkLabel(
            frame_modules, text="Aucun module.", justify="left", text_color="gray60"
        )
        self.lbl_modules_info.pack(anchor="w", padx=10, pady=(0, 8))

    def update(self, patch: dict | None) -> None:
        if patch:
            info = (
                f"Patch actuel : {patch['team']}\n"
                f"Installé le : {patch['install_date'][:10]}\n"
                f"Fichiers : {patch['file_count']}"
            )
            self.lbl_status_info.configure(text=info)

            modules = patch.get("modules", [])
            if modules:
                lines = "\n".join(
                    f"  • {m['name']}  ({m['file_count']} fichiers)"
                    for m in modules
                )
                self.lbl_modules_info.configure(text=lines, text_color=("gray20", "gray80"))
            else:
                self.lbl_modules_info.configure(text="Aucun module.", text_color="gray60")
        else:
            self.lbl_status_info.configure(text="Aucun patch n'est actuellement installé.")
            self.lbl_modules_info.configure(text="Aucun module.", text_color="gray60")
