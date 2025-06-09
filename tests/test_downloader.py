# интеграционный тест
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from yt_dl_cli.main import VideoDownloader
from yt_dl_cli.config.config import Config


def test_downloader_runs_with_minimal_config(mocker):
    """VideoDownloader start with minimal settings test"""
    # Мокаем весь yt_dlp чтобы не было настоящих запросов
    mock_ytdlp = mocker.patch("yt_dlp.YoutubeDL")
    instance = mock_ytdlp.return_value
    instance.__enter__.return_value.extract_info.return_value = {"title": "TestTitle"}
    instance.__enter__.return_value.download.return_value = None

    config = Config(
        save_dir="test_dir",  # type: ignore
        max_workers=1,
        quality="best",
        audio_only=False,
        urls=["https://youtu.be/test"],
    )
    downloader = VideoDownloader(config=config)
    try:
        downloader.download()
    except SystemExit:
        pass  # Для интеграционного теста окей
    assert mock_ytdlp.called
