import customtkinter as ctk

from ..config import ConfigManager
from ..constants import APPDATA_DIR, APPDATA_DIR_TEST, LOG_FILE, LOG_FILE_TEST, CONFIG_FILE_TEST
from ..fs_ops import AbstractFileSystemOps, DryRunFileSystemOps, RealFileSystemOps
from ..installer import InstallService
from ..logger import Logger
from ..version import __version__
from .tab_accueil import TabAccueil
from .tab_install import TabInstall
from .tab_log import TabLog
from .tab_modules import TabModules
from .tab_param import TabParam
from .tab_uninst import TabUninst

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PatchManagerApp(ctk.CTk):
    def __init__(self, test_mode: bool = False):
        super().__init__()

        self.test_mode = test_mode
        self.is_processing = False

        self.title(f"Patch Manager - eFootball  v{__version__}")
        self.geometry("900x720")
        self.minsize(700, 500)

        # Répertoires selon le mode
        appdata_dir = APPDATA_DIR_TEST if test_mode else APPDATA_DIR
        log_file = LOG_FILE_TEST if test_mode else LOG_FILE
        config_file = CONFIG_FILE_TEST if test_mode else None

        # Services
        self.config_manager = ConfigManager(config_file) if config_file else ConfigManager()
        self.logger = Logger(log_file)
        self._log_file = log_file

        config_data = self.config_manager.load()
        if test_mode:
            self.fs_ops: AbstractFileSystemOps = DryRunFileSystemOps(
                game_path=config_data.get("game_path", ""),
                archive_path="",
            )
        else:
            self.fs_ops = RealFileSystemOps()

        self.install_service = InstallService(
            config_manager=self.config_manager,
            fs_ops=self.fs_ops,
            logger=self.logger,
            progress_callback=self.set_progress,
            appdata_dir=appdata_dir,
        )

        self._build_ui()
        self.logger.set_ui_callback(self._on_log_line)
        self.update_ui()

    # ------------------------------------------------------------------
    # Construction UI
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        # HEADER
        self.header = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=("gray80", "gray15"))
        self.header.pack(side="top", fill="x")

        title_text = f"Patch Manager eFootball  v{__version__}"
        self.lbl_title = ctk.CTkLabel(
            self.header, text=title_text, font=ctk.CTkFont(size=20, weight="bold")
        )
        self.lbl_title.pack(side="left", padx=20, pady=15)

        if self.test_mode:
            ctk.CTkLabel(
                self.header,
                text="[MODE TEST]",
                text_color="white",
                fg_color="#fd7e14",
                corner_radius=5,
                padx=8,
                pady=4,
            ).pack(side="left", padx=8, pady=15)

        self.lbl_badge = ctk.CTkLabel(
            self.header,
            text="AUCUN PATCH",
            text_color="white",
            fg_color="gray50",
            corner_radius=5,
            padx=10,
            pady=5,
        )
        self.lbl_badge.pack(side="right", padx=20, pady=15)

        # FOOTER
        self.footer = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color=("gray80", "gray15"))
        self.footer.pack(side="bottom", fill="x")

        self.lbl_progress = ctk.CTkLabel(self.footer, text="Prêt.", anchor="w")
        self.lbl_progress.pack(side="left", padx=20, fill="x", expand=True)

        self.progressbar = ctk.CTkProgressBar(self.footer, width=300)
        self.progressbar.pack(side="right", padx=20)
        self.progressbar.set(0)

        # TABS
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        tab_acc = self.tabview.add("Accueil")
        tab_ins = self.tabview.add("Installer")
        tab_mod = self.tabview.add("Modules")
        tab_uni = self.tabview.add("Désinstaller")
        tab_par = self.tabview.add("Paramètres")
        tab_log = self.tabview.add("Journal")

        self._tab_accueil = TabAccueil(tab_acc)
        self._tab_install = TabInstall(tab_ins, self)
        self._tab_modules = TabModules(tab_mod, self)
        self._tab_uninst = TabUninst(tab_uni, self)
        self._tab_param = TabParam(tab_par, self)
        self._tab_log = TabLog(tab_log, self._log_file)

    # ------------------------------------------------------------------
    # Mise à jour UI
    # ------------------------------------------------------------------
    def update_ui(self) -> None:
        config_data = self.config_manager.load()
        patch = config_data.get("current_patch")

        self._tab_param.load_values(config_data)
        self._tab_accueil.update(patch)
        self._tab_uninst.update(patch)
        self._tab_modules.update(patch)

        if patch:
            fg = "#007bff" if patch["team"] == "evomod" else "#fd7e14"
            self.lbl_badge.configure(text=patch["team"].upper(), fg_color=fg)
        else:
            self.lbl_badge.configure(text="AUCUN PATCH", fg_color="gray50")

        # Sync game_path dans DryRunFileSystemOps si nécessaire
        if self.test_mode and isinstance(self.fs_ops, DryRunFileSystemOps):
            self.fs_ops._game_path = config_data.get("game_path", "")

    def set_progress(self, percent: float, text: str) -> None:
        self.after(0, lambda: self.progressbar.set(percent))
        self.after(0, lambda: self.lbl_progress.configure(text=text))

    def _on_log_line(self, line: str) -> None:
        self.after(0, lambda: self._tab_log.append(line))
