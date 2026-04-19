# Contributing — eFootball Patch Manager

Merci de l'intérêt pour ce projet !  
Ce guide explique comment contribuer, tester et publier une release.

---

## Prérequis

- Python 3.10+
- Git

## Installation de l'environnement de développement

```bash
git clone https://github.com/devcfk/eFootball-Patch-Manager.git
cd eFootball-Patch-Manager

python -m venv .venv
.venv\Scripts\activate

pip install customtkinter darkdetect py7zr rarfile pytest pyinstaller
```

---

## Lancer l'application

```bash
# Mode normal
python main.py

# Mode test (aucun fichier du jeu modifié)
python main.py --test
```

---

## Lancer les tests

```bash
python -m pytest tests/ -v
```

Les tests utilisent `DryRunFileSystemOps` — aucun fichier réel n'est touché.

---

## Proposer une modification

1. Fork le dépôt
2. Crée une branche depuis `develop` :
   ```bash
   git checkout -b feature/ma-fonctionnalite
   ```
3. Fais tes modifications et teste-les (`python main.py --test` + pytest)
4. Ouvre une **Pull Request** vers la branche `develop`

> La branche `main` est réservée aux releases stables.

---

## Versioning

Ce projet suit le **versioning sémantique** ([SemVer](https://semver.org/)) :

| Type | Exemple | Quand |
|------|---------|-------|
| MAJOR | `2.0.0` | Rupture de la structure de config ou refonte complète de l'UI |
| MINOR | `1.1.0` | Nouvelle fonctionnalité (nouvel onglet, nouveau format d'archive…) |
| PATCH | `1.0.1` | Correction de bug, fix de traduction, mise à jour de dépendance |

La version est définie dans un seul endroit : [`patch_manager/version.py`](patch_manager/version.py).

---

## Publier une release (mainteneur)

> Les livrables (`.exe`, dossier portable) ne sont **jamais commités** dans le dépôt.  
> Ils sont générés localement et attachés à une GitHub Release.

1. Mettre à jour la version :
   ```python
   # patch_manager/version.py
   __version__ = "X.Y.Z"
   ```

2. Mettre à jour le `README.md` (section Changelog)

3. Commiter et tagger :
   ```bash
   git add patch_manager/version.py README.md
   git commit -m "chore: release vX.Y.Z"
   git tag vX.Y.Z
   git push origin develop --tags
   ```

4. Générer les livrables :
   ```bash
   build.bat
   ```
   Produit dans `dist/` :
   - `eFootball Patch Manager/` → zipper en `eFootball_PatchManager_X.Y.Z_portable.zip`
   - `eFootball_PatchManager_X.Y.Z_Setup.exe` (nécessite [Inno Setup](https://jrsoftware.org/isinfo.php))

5. Créer la release sur GitHub :
   - Aller sur **Releases → Draft a new release**
   - Sélectionner le tag `vX.Y.Z`
   - Attacher les deux fichiers générés
   - Publier

---

## Structure du projet

```
eFootball Patch Manager/
├── main.py                     # Point d'entrée
├── build.bat                   # Script de build des livrables
├── eFootball_PatchManager.spec # Config PyInstaller
├── installer/
│   └── setup.iss               # Script Inno Setup
├── patch_manager/
│   ├── version.py              # Source unique de la version
│   ├── constants.py
│   ├── config.py
│   ├── logger.py
│   ├── fs_ops.py
│   ├── installer.py
│   └── ui/
│       ├── app.py
│       ├── tab_accueil.py
│       ├── tab_install.py
│       ├── tab_modules.py
│       ├── tab_uninst.py
│       ├── tab_history.py
│       ├── tab_param.py
│       └── tab_log.py
└── tests/
    ├── test_config.py
    └── test_installer.py
```

---

## Ce qu'il ne faut pas commiter

Les entrées suivantes sont dans `.gitignore` et ne doivent jamais être poussées :

| Entrée | Raison |
|--------|--------|
| `.venv/` | Environnement virtuel local |
| `build/`, `dist/` | Artefacts de build — regénérés via `build.bat` |
| `__pycache__/`, `*.pyc` | Bytecode Python |
| `.pytest_cache/` | Cache pytest |
| `.vscode/`, `.idea/`, `.claude/` | Config IDE locale |
