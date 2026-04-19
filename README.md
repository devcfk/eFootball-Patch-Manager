# Patch Manager — eFootball

**Outil de gestion des patches pour eFootball** (evomod / ePatch)  
**Patch management tool for eFootball**

---

## Prérequis / Prerequisites

- **Python 3.10+**
- **7-Zip** (optionnel, recommandé pour les performances) — [7-zip.org](https://www.7-zip.org/)
- Dépendances Python :

```bash
pip install customtkinter darkdetect py7zr rarfile
```

> Sans 7-Zip installé, les archives ZIP, 7Z et RAR sont gérées nativement via `py7zr` et `rarfile`.

---

## Installation

```bash
# Cloner ou télécharger le projet
cd "eFootball Patch Manager"

# (Optionnel) Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate

pip install customtkinter darkdetect py7zr rarfile
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
Toutes les opérations sur le disque (copie, suppression, extraction) sont simulées et tracées dans un journal d'opérations.  
La configuration et les logs sont écrits dans un répertoire AppData isolé (`eFootball_PatchManager_Test`) pour ne pas polluer les données du mode normal.

Un bandeau orange **[MODE TEST]** s'affiche dans l'interface pour éviter toute confusion.

> In test mode, all filesystem operations (copy, delete, extraction) are simulated. No game files are touched. Config and logs are written to a separate AppData directory. A visible `[MODE TEST]` banner is shown in the UI.

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
│   ├── logger.py               # Logger avec callback UI et séparateurs de session
│   ├── fs_ops.py               # Opérations FS (Real + DryRun pour le mode test)
│   ├── installer.py            # Service d'installation/désinstallation (patch + modules)
│   └── ui/
│       ├── app.py              # Fenêtre principale, injection des services
│       ├── tab_accueil.py      # Onglet Accueil — statut patch + modules actifs
│       ├── tab_install.py      # Onglet Installer — installation du patch principal
│       ├── tab_modules.py      # Onglet Modules — installation de modules additionnels
│       ├── tab_uninst.py       # Onglet Désinstaller — restauration + suppression backup
│       ├── tab_history.py      # Onglet Historique — patches désinstallés par le passé
│       ├── tab_param.py        # Onglet Paramètres — chemins jeu, backup, 7-Zip
│       └── tab_log.py          # Onglet Journal — colorisé, filtrable par niveau
│
└── tests/
    ├── test_config.py
    └── test_installer.py       # Tests sans UI via DryRunFileSystemOps
```

---

## Fonctionnalités / Features

- **Installation de patch principal** (ZIP / 7Z / RAR) avec backup automatique des fichiers remplacés
- **Modules additionnels** : installation de fichiers complémentaires sur un patch de base, avec chemin d'installation personnalisable par module
- **Désinstallation complète** : restauration des fichiers originaux en ordre inverse (modules puis patch), avec option de suppression automatique des backups
- **Historique** : consultation des patches précédemment désinstallés avec leurs détails
- **Journal colorisé** : niveaux OK / ERROR / WARNING / INFO différenciés par couleur, filtres Tout / Résumé / Erreurs, séparateurs de session
- **Mode test** : simulation complète sans toucher au disque
- **Séparateurs de chemin** : tous les chemins sont normalisés en `/` en interne, affichés en `\` dans l'interface Windows

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
| MINOR | `1.1.0` | Nouvelle fonctionnalité (nouvel onglet, nouveau format d'archive…) |
| PATCH | `1.0.1` | Correction de bug, fix de traduction, mise à jour de dépendance |

La version est définie dans [`patch_manager/version.py`](patch_manager/version.py) et affichée dans le titre de la fenêtre.

---

## Changelog

### v1.1.0 — 2026-04-19
- Onglet **Modules** : installation de modules additionnels sur un patch de base, chemin d'installation personnalisable, nom déduit du fichier archive
- Onglet **Historique** : liste des patches désinstallés avec détails et copie du chemin backup
- **Journal amélioré** : colorisation par niveau, filtres Tout / Résumé / Erreurs, séparateurs de session par opération
- **Suppression automatique des backups** après désinstallation (option cochée par défaut)
- Affichage du chemin backup complet (format Windows) dans l'onglet Désinstaller avec bouton copier
- Nom du dossier backup module enrichi du nom du module (`module_0_Faces Pack v2_2026-04-18_...`)
- Support natif ZIP / 7Z / RAR via `py7zr` et `rarfile` (7-Zip devient optionnel)
- Normalisation de tous les séparateurs de chemin en `/` (affichage `\` dans l'UI)
- Lien de téléchargement 7-Zip dans l'onglet Paramètres
- Isolation complète des données mode test (`eFootball_PatchManager_Test`)
- Logs détaillés fichier par fichier : `[REMPLACÉ]`, `[AJOUTÉ]`, `[SUPPRIMÉ]`, `[RESTAURÉ]`

### v1.0.0 — 2026-04-18
- Refactorisation en modules interconnectés (`config`, `logger`, `fs_ops`, `installer`, `ui/`)
- Ajout du mode test `--test` (simulation sans modification du disque)
- Système de versioning sémantique
- Tests unitaires via `pytest` (sans UI)
- README bilingue FR/EN

---

## Licence

Usage personnel. Projet non officiel, sans affiliation avec Konami.
