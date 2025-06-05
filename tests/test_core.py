import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import pytest

from yt_dl_cli.core.core import VideoInfoExtractor, DownloadExecutor
from yt_dl_cli.interfaces.interfaces import ILogger


class DummyLogger(ILogger):
    def __init__(self):
        self.messages = []

    def error(self, msg):
        self.messages.append(msg)

    def info(self, msg):
        self.messages.append(msg)

    def warning(self, msg):
        self.messages.append(msg)

    def critical(self, msg):
        self.messages.append(msg)


def test_extract_info_logs_error(mocker):
    dummy_logger = DummyLogger()
    mocker.patch("yt_dlp.YoutubeDL", side_effect=Exception("fail"))
    extractor = VideoInfoExtractor(logger=dummy_logger)
    info = extractor.extract_info("fakeurl", opts={})
    assert info is None
    assert any("fail" in msg for msg in dummy_logger.messages)


def test_download_executor_handles_error(mocker):
    dummy_logger = DummyLogger()
    mocker.patch("yt_dlp.YoutubeDL", side_effect=Exception("fail"))
    executor = DownloadExecutor(logger=dummy_logger)
    result = executor.execute_download("fakeurl", opts={})
    assert result is False
    assert any("fail" in msg for msg in dummy_logger.messages)
