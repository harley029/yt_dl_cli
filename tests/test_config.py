import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from yt_dl_cli.utils.parser import parse_arguments


def test_config_parsing_from_args(monkeypatch):
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
    monkeypatch.setattr("pathlib.Path.read_text", lambda *a, **kw: "")
    sys.argv = ["yt-dl-cli"]
    config = parse_arguments()
    assert config.urls == []
    assert str(config.save_dir) == "downloads"
    assert config.quality == "best"
    assert config.max_workers == 2
    assert config.audio_only is False
