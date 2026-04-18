import os
import tempfile

from patch_manager.config import ConfigManager
from patch_manager.fs_ops import DryRunFileSystemOps
from patch_manager.installer import InstallService
from patch_manager.logger import Logger


def _make_service(tmpdir: str, game_path: str = "C:/Games/eFootball"):
    config_path = os.path.join(tmpdir, "config.json")
    cfg = ConfigManager(config_path)
    data = cfg.load()
    data["game_path"] = game_path
    data["backup_root"] = os.path.join(tmpdir, "backups")
    cfg.save(data)

    log_file = os.path.join(tmpdir, "test.log")
    logger = Logger(log_file)

    progress_calls = []
    fs_ops = DryRunFileSystemOps(game_path=game_path, archive_path="fake.zip")

    service = InstallService(
        config_manager=cfg,
        fs_ops=fs_ops,
        logger=logger,
        progress_callback=lambda p, t: progress_calls.append((p, t)),
        appdata_dir=tmpdir,
    )
    return service, cfg, fs_ops, progress_calls


def test_install_dry_run_does_not_touch_disk():
    with tempfile.TemporaryDirectory() as tmpdir:
        service, cfg, fs_ops, progress_calls = _make_service(tmpdir)
        service.install("evomod", "fake.zip")

        # Vérifier que des opérations ont été loguées sans rien créer dans le game_path
        assert len(fs_ops.operations_log) > 0
        ops = [op["op"] for op in fs_ops.operations_log]
        assert "copy2" in ops or "extract" in ops

        # Config doit être mise à jour
        data = cfg.load()
        assert data["current_patch"] is not None
        assert data["current_patch"]["team"] == "evomod"
        assert data["current_patch"]["file_count"] > 0

        # La progression doit être montée jusqu'à 1.0
        final_progresses = [p for p, _ in progress_calls]
        assert max(final_progresses) == 1.0


def test_uninstall_dry_run_clears_patch():
    with tempfile.TemporaryDirectory() as tmpdir:
        service, cfg, fs_ops, _ = _make_service(tmpdir)
        service.install("ePatch", "fake.zip")

        data = cfg.load()
        assert data["current_patch"] is not None

        service.uninstall(silent=True)

        data = cfg.load()
        assert data["current_patch"] is None
        assert len(data["history"]) == 1
        assert data["history"][0]["team"] == "ePatch"


def test_install_then_reinstall_via_uninstall():
    with tempfile.TemporaryDirectory() as tmpdir:
        service, cfg, fs_ops, _ = _make_service(tmpdir)
        service.install("evomod", "fake.zip")
        service.uninstall(silent=True)
        service.install("ePatch", "fake.zip")

        data = cfg.load()
        assert data["current_patch"]["team"] == "ePatch"
        assert len(data["history"]) == 1
