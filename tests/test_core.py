from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import pytest

from yt_dl_cli.core.core import VideoInfoExtractor, DownloadExecutor
from yt_dl_cli.interfaces.interfaces import ILogger


class DummyLogger(ILogger):
    """Logger for tests"""
    def __init__(self):
        """init Logger for tests"""
        self.messages = []

    def error(self, msg):
        """Log error messages"""
        self.messages.append(msg)

    def info(self, msg):
        """Log info messages"""
        self.messages.append(msg)

    def warning(self, msg):
        """Log warning messages"""
        self.messages.append(msg)

    def critical(self, msg):
        """Log critical messages"""
        self.messages.append(msg)


def test_extract_info_logs_error(mocker):
    """Test VideoInfoExtractor logs error when extracting info"""
    dummy_logger = DummyLogger()
    mocker.patch("yt_dlp.YoutubeDL", side_effect=Exception("fail"))
    extractor = VideoInfoExtractor(logger=dummy_logger)
    info = extractor.extract_info("fakeurl", opts={})
    assert info is None
    assert any("fail" in msg for msg in dummy_logger.messages)


def test_download_executor_handles_error(mocker):
    """Test DownloadExecutor handles exceptions"""
    dummy_logger = DummyLogger()
    mocker.patch("yt_dlp.YoutubeDL", side_effect=Exception("fail"))
    executor = DownloadExecutor(logger=dummy_logger)
    result = executor.execute_download("fakeurl", opts={})
    assert result is False
    assert any("fail" in msg for msg in dummy_logger.messages)


def test_downloadercore_exit_handles_exceptions(monkeypatch):
    """Test DownloaderCore.exit() handles exceptions"""
    import yt_dl_cli.core.core as core

    class DummyLogger:
        def __init__(self):
            self.warnings = []

        def warning(self, msg):
            self.warnings.append(msg)

    class DummyResource:
        def close(self):
            raise Exception("fail-close")

    logger = DummyLogger()
    dummy_config = object()
    core_obj = core.DownloaderCore(
        config=dummy_config,  # type: ignore
        strategy=None,  # type: ignore
        stats=None,  # type: ignore
        logger=logger,  # type: ignore
        file_checker=None,  # type: ignore
        info_extractor=None,  # type: ignore
        download_executor=None,  # type: ignore
    )  # type: ignore
    core_obj.register_resource(DummyResource())
    # Вызываем exit, проверяем, что logger.warning вызван:
    core_obj.__exit__(None, None, None)
    assert logger.warnings


class DummyLogger2:
    """Logger for tests"""
    def __init__(self):
        self.errors = []

    def error(self, msg):
        self.errors.append(msg)


def make_executor(monkeypatch, error_type):
    """Make DownloadExecutor with mocked YoutubeDL"""
    import yt_dl_cli.core.core as core

    logger = DummyLogger2()

    class DummyYDL:
        def __enter__(self):
            return self

        def __exit__(self, *a, **k):
            return False

        def download(self, urls):
            if error_type == "download":
                raise core.yt_dlp.DownloadError("fail-download")
            if error_type == "other":
                raise RuntimeError("fail-other")
            return 0

    monkeypatch.setattr(core.yt_dlp, "YoutubeDL", lambda opts: DummyYDL())
    return core.DownloadExecutor(logger), logger  # type: ignore


def test_execute_download_success(monkeypatch):
    """Test DownloadExecutor.execute_download() with success"""
    executor, logger = make_executor(monkeypatch, None)
    assert executor.execute_download("url", {}) is True


def test_execute_download_downloaderror(monkeypatch):
    """Test DownloadExecutor.execute_download() with DownloadError"""
    executor, logger = make_executor(monkeypatch, "download")
    assert executor.execute_download("url", {}) is False
    assert logger.errors


def test_execute_download_other(monkeypatch):
    """Test DownloadExecutor.execute_download() with other error"""
    executor, logger = make_executor(monkeypatch, "other")
    assert executor.execute_download("url", {}) is False
    assert logger.errors


class DummyLogger3:
    """Logger for tests"""
    def __init__(self):
        """init Logger for tests"""
        self.errors = []

    def error(self, msg):
        """Log error messages"""
        self.errors.append(msg)


def make_extractor(monkeypatch, error_type):
    """Make VideoInfoExtractor with mocked YoutubeDL"""
    import yt_dl_cli.core.core as core

    logger = DummyLogger3()

    class DummyYDL:
        def __enter__(self):
            return self

        def __exit__(self, *a, **k):
            return False

        def extract_info(self, url, download=False):
            if error_type == "none":
                return None
            if error_type == "download":
                raise core.yt_dlp.DownloadError("fail-download")
            if error_type == "extractor":
                raise core.yt_dlp.utils.ExtractorError("fail-extractor")
            if error_type == "other":
                raise RuntimeError("fail-other")
            return {"title": "OK"}

    monkeypatch.setattr(core.yt_dlp, "YoutubeDL", lambda opts: DummyYDL())
    return core.VideoInfoExtractor(logger), logger  # type: ignore


def test_extract_info_none(monkeypatch):
    """Test VideoInfoExtractor.extract_info() with None"""
    extractor, logger = make_extractor(monkeypatch, "none")
    info = extractor.extract_info("url", {})
    assert info is None
    assert logger.errors


def test_extract_info_downloaderror(monkeypatch):
    """Test VideoInfoExtractor.extract_info() with DownloadError """
    extractor, logger = make_extractor(monkeypatch, "download")
    info = extractor.extract_info("url", {})
    assert info is None
    assert logger.errors


def test_extract_info_extractorerror(monkeypatch):
    """Test VideoInfoExtractor.extract_info() with ExtractorError """
    extractor, logger = make_extractor(monkeypatch, "extractor")
    info = extractor.extract_info("url", {})
    assert info is None
    assert logger.errors


def test_extract_info_other(monkeypatch):
    """Test VideoInfoExtractor.extract_info() with other error """
    extractor, logger = make_extractor(monkeypatch, "other")
    info = extractor.extract_info("url", {})
    assert info is None
    assert logger.errors


@pytest.mark.parametrize(
    "info, file_exists, expect_failure, expect_skip",
    [
        (None, False, True, False),  # Случай: инфы нет → фейл
        ({"title": "Test Video"}, True, False, True),  # Случай: файл уже есть → скип
    ],
)
def test_download_single_branches(info, file_exists, expect_failure, expect_skip):
    """Test DownloaderCore.download_single() with branches"""
    from yt_dl_cli.core.core import DownloaderCore
    from yt_dl_cli.i18n.messages import Messages

    called = {
        "failure": 0,
        "skip": 0,
        "info": [],
    }

    class DummyStrategy:
        def get_opts(self):
            return {}

    class DummyStats:
        def record_failure(self):
            called["failure"] += 1

        def record_skip(self):
            called["skip"] += 1

        def record_success(self):
            pass

    class DummyLogger:
        def info(self, msg):
            called["info"].append(msg)

    class DummyFileChecker:
        def exists(self, path):
            return file_exists

    class DummyInfoExtractor:
        def extract_info(self, url, opts):
            return info

    class DummyDownloadExecutor:
        def execute_download(self, url, opts):
            return True

    # Мокаем config
    class DummyConfig:
        audio_only = False
        save_dir = Path(".")

    core = DownloaderCore(
        config=DummyConfig(),  # type: ignore
        strategy=DummyStrategy(),  # type: ignore
        stats=DummyStats(),  # type: ignore
        logger=DummyLogger(),  # type: ignore
        file_checker=DummyFileChecker(),  # type: ignore
        info_extractor=DummyInfoExtractor(),  # type: ignore
        download_executor=DummyDownloadExecutor(),  # type: ignore
    )

    core.download_single("https://some.url/test")

    if expect_failure:
        assert called["failure"] == 1
    else:
        assert called["failure"] == 0

    if expect_skip:
        assert called["skip"] == 1
        # Проверяем что был вызван правильный текст для logger.info
        assert any(
            Messages.Core.SKIP_EXISTS(title="Test Video") in m for m in called["info"]
        )
    else:
        assert called["skip"] == 0
