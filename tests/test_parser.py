import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from yt_dl_cli.utils.parser import parse_arguments


def test_parse_arguments_basic(monkeypatch):
    sys.argv = [
        "yt-dl-cli",
        "--urls",
        "https://a.com",
        "-d",
        "videos",
        "-q",
        "720",
        "-w",
        "3",
        "-a",
    ]
    config = parse_arguments()
    assert config.urls == ["https://a.com"]
    assert str(config.save_dir) == "videos"
    assert config.quality == "720"
    assert config.max_workers == 3
    assert config.audio_only is True
