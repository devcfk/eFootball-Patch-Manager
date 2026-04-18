# Patch Manager — eFootball 2026

**Outil de gestion des patches pour eFootball 2026** (evomod / ePatch)  
**Patch management tool for eFootball 2026**

---

## Prérequis / Prerequisites

- **Python 3.10+**
- **7-Zip** installé (recommandé pour les archives RAR et 7Z) — [7-zip.org](https://www.7-zip.org/)
- Dépendances Python :

```bash
pip install customtkinter darkdetect
```

---

## Installation

```bash
# Cloner ou télécharger le projet
cd "eFootball Patch Manager"

# (Optionnel) Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate

pip install customtkinter darkdetect
```

---

## Utilisation / Usage

```bash
# Mode normal
python main.py

# Mode test (aucune modification des fichiers du jeu)
python main.py --test
```

---

## Mode Test

En mode test (`--test`), **aucun fichier du jeu n'est modifié**.  
Toutes les opérations sur le disque (copie, suppression, extraction) sont simulées et tracées dans un journal d'opérations. La configuration et les logs sont écrits normalement pour permettre de vérifier le comportement sans risque.

Un bandeau orange **[MODE TEST]** s'affiche dans l'interface pour éviter toute confusion.

> In test mode, all filesystem operations (copy, delete, extraction) are simulated. No game files are touched. A visible `[MODE TEST]` banner is shown in the UI.

---

## Structure du projet / Project Structure

```
eFootball Patch Manager/
├── main.py                     # Point d'entrée / Entry point
├── pyproject.toml              # Métadonnées projet
├── README.md
│
├── patch_manager/              # Package principal
│   ├── version.py              # Version sémantique
│   ├── constants.py            # Chemins et constantes globales
│   ├── config.py               # Lecture/écriture de la configuration JSON
│   ├── logger.py               # Logger avec callback UI
│   ├── fs_ops.py               # Opérations FS (Real + DryRun pour le mode test)
│   ├── installer.py            # Service d'installation/désinstallation
│   └── ui/
│       ├── app.py              # Fenêtre principale, injection des services
│       ├── tab_accueil.py      # Onglet Accueil
│       ├── tab_install.py      # Onglet Installer
│       ├── tab_uninst.py       # Onglet Désinstaller
│       ├── tab_param.py        # Onglet Paramètres
│       └── tab_log.py          # Onglet Journal
│
└── tests/
    ├── test_config.py
    └── test_installer.py       # Tests sans UI via DryRunFileSystemOps
```

---

## Lancer les tests / Run Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## Versioning

Ce projet suit le **versionnage sémantique** ([SemVer](https://semver.org/)) :

| Type | Exemple | Quand |
|------|---------|-------|
| MAJOR | `2.0.0` | Rupture de la structure de config ou refonte complète de l'UI |
| MINOR | `1.1.0` | Nouvelle fonctionnalité (nouveau format d'archive, nouvel onglet…) |
| PATCH | `1.0.1` | Correction de bug, fix de traduction, mise à jour de dépendance |

La version est définie dans [`patch_manager/version.py`](patch_manager/version.py) et affichée dans le titre de la fenêtre.

---

## Changelog

### v1.0.0 — 2026-04-18
- Refactorisation en modules interconnectés (`config`, `logger`, `fs_ops`, `installer`, `ui/`)
- Ajout du mode test `--test` (simulation sans modification du disque)
- Système de versioning sémantique
- Tests unitaires via `pytest` (sans UI)
- README bilingue FR/EN

---

## Licence

Usage personnel. Projet non officiel, sans affiliation avec Konami.
