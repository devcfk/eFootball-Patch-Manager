# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — eFootball Patch Manager
# Généré manuellement pour un contrôle précis des assets inclus.

import sys
from pathlib import Path

ROOT = Path(SPECPATH)
VENV_SITE = ROOT / ".venv" / "Lib" / "site-packages"

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # customtkinter embarque ses thèmes et assets (obligatoire)
        (str(VENV_SITE / "customtkinter"), "customtkinter"),
        # darkdetect embarque un binaire natif sur Windows
        (str(VENV_SITE / "darkdetect"), "darkdetect"),
    ],
    hiddenimports=[
        "customtkinter",
        "darkdetect",
        "py7zr",
        "rarfile",
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "_pytest", "unittest"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="eFootball Patch Manager",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,          # Pas de fenêtre console
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=None,              # Remplacer par "installer/icon.ico" si disponible
)

# --- Version portable : dossier onedir ---
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="eFootball Patch Manager",
)
