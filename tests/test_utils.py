import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from yt_dl_cli.utils.utils import FilenameSanitizer


def test_filename_sanitizer():
    bad = "Bad/File:Name*With|Chars?"
    clean = FilenameSanitizer.sanitize(bad)
    assert "/" not in clean
    assert ":" not in clean
    assert "*" not in clean
    assert "|" not in clean
    assert "?" not in clean
    assert len(clean) <= 100
