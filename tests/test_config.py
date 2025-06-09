import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from yt_dl_cli.config.config import Config
from yt_dl_cli.utils.parser import parse_arguments


def test_config_parsing_from_args():
    """ Test parsing config from command line arguments  """
    test_args = [
        "yt-dl-cli",
        "--urls",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "--dir",
        "test_videos",
        "--quality",
        "720",
        "--workers",
        "5",
        "--audio-only",
    ]
    sys.argv = test_args
    config = parse_arguments()

    assert config.urls == ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
    assert str(config.save_dir) == "test_videos"
    assert config.quality == "720"
    assert config.max_workers == 5
    assert config.audio_only is True


def test_config_default_values(monkeypatch):
    """ Test default config values  """
    monkeypatch.setattr("pathlib.Path.read_text", lambda *a, **kw: "")
    sys.argv = ["yt-dl-cli"]
    config = parse_arguments()
    assert config.urls == []
    assert str(config.save_dir) == "downloads"
    assert config.quality == "best"
    assert config.max_workers == 2
    assert config.audio_only is False


def test_config_invalid_workers():
    """ Test invalid max_workers value  """
    try:
        Config(
            save_dir="d",  # type: ignore
            max_workers=0,
            quality="best",
            audio_only=False,
            urls=[]
        )  # type: ignore
    except ValueError as e:
        assert "max_workers must be at least 1, got 0" == str(e)


def test_config_quality():
    """ Test invalid quality value  """
    try:
        Config(
            save_dir="d",  # type: ignore
            max_workers=2,
            quality="1080",
            audio_only=False,
            urls=[]
        )  # type: ignore
    except ValueError as e:
        assert "quality must be one of: best, worst, 720, 480, 360, got 1080" == str(e)
