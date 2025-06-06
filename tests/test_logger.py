from pathlib import Path
import logging

import pytest

from yt_dl_cli.utils.logger import LoggerFactory


def test_loggerfactory_mkdir_oserror(monkeypatch):
    # Патчим метод mkdir именно у класса PosixPath (или Path)
    def bad_mkdir(self, *a, **k):
        raise OSError("fail mkdir")

    monkeypatch.setattr(Path, "mkdir", bad_mkdir)
    dummy_path = Path("bad_dir")
    with pytest.raises(OSError) as excinfo:
        LoggerFactory.get_logger(dummy_path)
    assert "Failed to create log directory" in str(excinfo.value)


def test_loggerfactory_filehandler_permissionerror(monkeypatch, tmp_path):
    logging.getLogger().handlers.clear()
    orig_stream_handler = logging.StreamHandler

    def fake_filehandler(*a, **k):
        raise PermissionError("no write access")

    monkeypatch.setattr(logging, "FileHandler", fake_filehandler)
    monkeypatch.setattr(logging, "StreamHandler", orig_stream_handler)
    with pytest.raises(PermissionError) as excinfo:
        LoggerFactory.get_logger(tmp_path)
    assert "Cannot create log file" in str(excinfo.value)


def test_loggerfactory_ok(tmp_path):
    logging.getLogger().handlers.clear()
    logger = LoggerFactory.get_logger(tmp_path)
    assert logger.name == "video_dl_cli"
    log_file = tmp_path / "download.log"
    logger.info("Hello log!")
    assert log_file.exists()
    assert "Hello log" in log_file.read_text(encoding="utf-8")


def test_loggerfactory_double_config_no_duplicate_handlers(tmp_path):
    logging.getLogger().handlers.clear()
    logger1 = LoggerFactory.get_logger(tmp_path)
    logger2 = LoggerFactory.get_logger(tmp_path)
    root = logging.getLogger()
    assert len(root.handlers) >= 2
    assert logger1 is not None
    assert logger2 is not None
