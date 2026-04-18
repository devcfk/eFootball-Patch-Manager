import os
import tkinter as tk
from tkinter import font as tkfont

import customtkinter as ctk

# Mapping niveau → tag de couleur
_LEVEL_TAGS = {
    "OK":      "tag_ok",
    "ERROR":   "tag_error",
    "WARNING": "tag_warn",
    "INFO":    "tag_info",
}

# Tags liés aux mots-clés dans le message (indépendant du niveau)
_KEYWORD_TAGS = {
    "[REMPLACÉ]":        "tag_replaced",
    "[AJOUTÉ]":          "tag_added",
    "[SUPPRIMÉ]":        "tag_removed",
    "[RESTAURÉ]":        "tag_restored",
    "[BACKUP SUPPRIMÉ]": "tag_removed",
}

_FILTER_ALL     = "Tout"
_FILTER_SUMMARY = "Résumé"
_FILTER_ERRORS  = "Erreurs"


def _tag_for_line(line: str) -> str:
    """Retourne le tag de colorisation principal d'une ligne."""
    for kw, tag in _KEYWORD_TAGS.items():
        if kw in line:
            return tag
    if "][OK]"      in line: return "tag_ok"
    if "][ERROR]"   in line: return "tag_error"
    if "][WARNING]" in line: return "tag_warn"
    if "═" in line:          return "tag_separator"
    return "tag_info"


def _is_detail_line(line: str) -> bool:
    """Ligne de détail fichier = filtrée en mode Résumé."""
    return any(kw in line for kw in _KEYWORD_TAGS)


def _is_error_line(line: str) -> bool:
    return "][ERROR]" in line or "][WARNING]" in line


class TabLog:
    def __init__(self, parent: ctk.CTkFrame, log_file: str):
        self._log_file = log_file
        self._all_lines: list[str] = []
        self._filter = _FILTER_ALL

        # --- Barre de filtres ---
        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.pack(fill="x", padx=8, pady=(6, 2))
        ctk.CTkLabel(bar, text="Afficher :").pack(side="left", padx=(0, 8))

        self._filter_var = tk.StringVar(value=_FILTER_ALL)
        for label in (_FILTER_ALL, _FILTER_SUMMARY, _FILTER_ERRORS):
            ctk.CTkRadioButton(
                bar, text=label,
                variable=self._filter_var, value=label,
                command=self._on_filter_change,
            ).pack(side="left", padx=6)

        ctk.CTkButton(
            bar, text="Effacer l'affichage", width=130, height=26,
            command=self._clear_display,
        ).pack(side="right", padx=4)

        # --- Zone de texte (tkinter.Text natif pour les tags couleur) ---
        frame_txt = ctk.CTkFrame(parent)
        frame_txt.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        self._txt = tk.Text(
            frame_txt,
            font=("Consolas", 11),
            wrap="none",
            state="disabled",
            relief="flat",
            bd=0,
        )
        scrolly = tk.Scrollbar(frame_txt, orient="vertical",   command=self._txt.yview)
        scrollx = tk.Scrollbar(frame_txt, orient="horizontal", command=self._txt.xview)
        self._txt.configure(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)

        scrolly.pack(side="right",  fill="y")
        scrollx.pack(side="bottom", fill="x")
        self._txt.pack(fill="both", expand=True)

        self._apply_theme()
        self._define_tags()

        # Charge le fichier log existant
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    self._all_lines.append(line)
            self._redraw()

    # ------------------------------------------------------------------

    def _apply_theme(self) -> None:
        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            self._txt.configure(bg="#1e1e1e", fg="#d4d4d4", insertbackground="white",
                                selectbackground="#264f78")
        else:
            self._txt.configure(bg="#ffffff", fg="#1e1e1e", insertbackground="black",
                                selectbackground="#add6ff")

    def _define_tags(self) -> None:
        mode = ctk.get_appearance_mode()
        dark = (mode == "Dark")
        self._txt.tag_configure("tag_ok",        foreground="#4ec94e")
        self._txt.tag_configure("tag_error",      foreground="#f44747")
        self._txt.tag_configure("tag_warn",       foreground="#ce9178")
        self._txt.tag_configure("tag_info",       foreground="#9cdcfe" if dark else "#555555")
        self._txt.tag_configure("tag_replaced",   foreground="#e5c07b")
        self._txt.tag_configure("tag_added",      foreground="#56b6c2")
        self._txt.tag_configure("tag_removed",    foreground="#e06c75")
        self._txt.tag_configure("tag_restored",   foreground="#61afef")
        self._txt.tag_configure("tag_separator",
                                foreground="#ffffff" if dark else "#000000",
                                font=("Consolas", 11, "bold"))

    def _redraw(self) -> None:
        self._txt.configure(state="normal")
        self._txt.delete("1.0", "end")

        filt = self._filter_var.get()
        for line in self._all_lines:
            if filt == _FILTER_SUMMARY and _is_detail_line(line):
                continue
            if filt == _FILTER_ERRORS and not (_is_error_line(line) or "═" in line):
                continue
            tag = _tag_for_line(line)
            self._txt.insert("end", line, tag)

        self._txt.configure(state="disabled")
        self._txt.see("end")

    def _on_filter_change(self) -> None:
        self._redraw()

    def _clear_display(self) -> None:
        self._txt.configure(state="normal")
        self._txt.delete("1.0", "end")
        self._txt.configure(state="disabled")

    # ------------------------------------------------------------------
    # API publique appelée par app._on_log_line
    # ------------------------------------------------------------------

    def append(self, line: str) -> None:
        self._all_lines.append(line)
        filt = self._filter_var.get()
        if filt == _FILTER_SUMMARY and _is_detail_line(line):
            return
        if filt == _FILTER_ERRORS and not (_is_error_line(line) or "═" in line):
            return
        tag = _tag_for_line(line)
        self._txt.configure(state="normal")
        self._txt.insert("end", line, tag)
        self._txt.configure(state="disabled")
        self._txt.see("end")
