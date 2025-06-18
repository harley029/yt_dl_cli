import io
import os
import sys
from pathlib import Path
import argparse  

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from yt_dl_cli.i18n.messages import Messages
from yt_dl_cli.utils.parser import parse_arguments
from yt_dl_cli.utils.validators import ArgValidator


# Фикстура для временного файла с URL
@pytest.fixture
def url_file(tmp_path):
    file_path = tmp_path / "urls.txt"
    content = """
    https://youtube.com/watch?v=video1
    # Comment line
    https://youtube.com/watch?v=video2
    
    https://youtube.com/watch?v=video3
    """
    file_path.write_text(content, encoding="utf-8")
    return file_path


def test_parse_arguments_basic(monkeypatch):
    """Test parsing arguments with basic usage."""
    sys.argv = [
        "yt-dl-cli",
        "--urls",
        "https://youtube.com/watch?v=video1",
        "-d",
        "videos",
        "-q",
        "720",
        "-w",
        "3",
        "-a",
    ]
    config = parse_arguments()
    assert config.urls == ["https://youtube.com/watch?v=video1"]
    assert str(config.save_dir) == "videos"
    assert config.quality == "720"
    assert config.max_workers == 3
    assert config.audio_only is True


def test_parse_arguments_with_file(url_file, monkeypatch):
    """Test parsing arguments with a URL file."""
    sys.argv = [
        "yt-dl-cli",
        "-f",
        str(url_file),
        "-d",
        "downloads",
        "-q",
        "best",
        "-w",
        "2",
    ]
    config = parse_arguments()
    assert config.urls == [
        "https://youtube.com/watch?v=video1",
        "https://youtube.com/watch?v=video2",
        "https://youtube.com/watch?v=video3",
    ]
    assert str(config.save_dir) == "downloads"
    assert config.quality == "best"
    assert config.max_workers == 2
    assert config.audio_only is False


def test_parse_arguments_urls_override_file(url_file, monkeypatch):
    """Test that --urls overrides --file."""
    sys.argv = [
        "yt-dl-cli",
        "-f",
        str(url_file),
        "--urls",
        "https://youtube.com/watch?v=override",
    ]
    config = parse_arguments()
    assert config.urls == ["https://youtube.com/watch?v=override"]


def test_validate_workers_valid():
    """Test valid worker counts."""
    assert ArgValidator.validate_workers("5") == 5
    assert ArgValidator.validate_workers("1") == 1
    assert ArgValidator.validate_workers("10") == 10


def test_validate_workers_invalid(monkeypatch):
    """Test invalid worker counts."""
    sys.argv = ["yt-dl-cli", "-w", "0"]
    with pytest.raises(SystemExit):
        parse_arguments()

    sys.argv = ["yt-dl-cli", "-w", "11"]
    with pytest.raises(SystemExit):
        parse_arguments()

    sys.argv = ["yt-dl-cli", "-w", "invalid"]
    with pytest.raises(SystemExit):
        parse_arguments()


def test_validate_directory_valid(tmp_path):
    """Test valid directory paths."""
    dir_path = tmp_path / "downloads"
    assert ArgValidator.validate_directory(str(dir_path)) == dir_path
    assert dir_path.exists()


def test_validate_directory_invalid():
    """Test invalid directory paths."""
    with pytest.raises(argparse.ArgumentTypeError):
        ArgValidator.validate_directory("/nonexistent/invalid/path")


def test_validate_quality_valid():
    """Test valid quality settings."""
    valid_qualities = ["best", "worst", "1080", "720", "480", "360"]
    for quality in valid_qualities:
        assert ArgValidator.validate_quality(quality) == quality


def test_validate_quality_invalid(monkeypatch):
    """Test invalid quality settings."""
    sys.argv = ["yt-dl-cli", "-q", "invalid"]
    with pytest.raises(SystemExit):
        parse_arguments()


def test_validate_url_file_valid(url_file):
    """Test valid URL file."""
    assert ArgValidator.validate_url_file(str(url_file)) == url_file


def test_validate_url_file_invalid():
    """Test invalid URL file."""
    with pytest.raises(argparse.ArgumentTypeError):
        ArgValidator.validate_url_file("nonexistent.txt")

    with pytest.raises(argparse.ArgumentTypeError):
        # Создаем пустой файл
        with open("empty.txt", "w") as f:
            pass
        try:
            ArgValidator.validate_url_file("empty.txt")
        finally:
            os.remove("empty.txt")


def test_validate_url_list_valid():
    """Test valid URL list."""
    urls = ["https://youtube.com/watch?v=video1", "http://example.com"]
    assert ArgValidator.validate_url_list(urls) == urls


def test_validate_url_list_invalid():
    """Test invalid URL list."""
    with pytest.raises(argparse.ArgumentTypeError):
        ArgValidator.validate_url_list([])

    with pytest.raises(argparse.ArgumentTypeError):
        ArgValidator.validate_url_list(["invalid_url"])

    with pytest.raises(argparse.ArgumentTypeError):
        ArgValidator.validate_url_list(["ftp://invalid.com"])


def run_with_file_error(monkeypatch, error, url_file):
    """Run parse_arguments with file-related error."""
    sys.argv = ["yt-dl-cli", "-f", str(url_file)]

    monkeypatch.setattr(
        Path, "read_text", lambda self, encoding=None: (_ for _ in ()).throw(error)
    )

    stderr = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = stderr

    config = parse_arguments()

    sys.stderr = old_stderr
    return config, stderr.getvalue()


@pytest.mark.parametrize(
    "exc_type, exc_args, expected_part",
    [
        (FileNotFoundError, (), "not found"),
        (PermissionError, (), "Permission denied"),
        (
            UnicodeDecodeError,
            ("utf-8", b"\x80", 0, 1, "invalid start byte"),
            "Encoding error",
        ),
        (IsADirectoryError, (), "Is a directory"),
        (OSError, (), "OS error"),
        (ValueError, (), "Value error"),
        (Exception, ("Some error",), "Error reading"),
    ],
)
def test_parse_arguments_all_exceptions(
    monkeypatch, exc_type, exc_args, expected_part, url_file
):
    """Test parsing arguments with various file-related exceptions."""

    def raise_exc(*a, **kw):
        raise exc_type(*exc_args)

    monkeypatch.setattr(Path, "read_text", raise_exc)

    printed = {}

    def fake_print(*args, file=None, **kwargs):
        printed["msg"] = args[0] if args else ""
        printed["file"] = file

    monkeypatch.setattr("builtins.print", fake_print)

    sys.argv = ["yt-dl-cli", "--file", str(url_file)]
    config = parse_arguments()

    assert config.urls == []
    assert (
        expected_part in printed["msg"]
        or Messages.CLI.FILE_NOT_FOUND(file=str(url_file)) in printed["msg"]
    )
    assert printed["file"] == sys.stderr
