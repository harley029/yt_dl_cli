import io
from pathlib import Path
import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from yt_dl_cli.i18n.messages import Messages
from yt_dl_cli.utils.parser import parse_arguments


def test_parse_arguments_basic(monkeypatch):
    """ Test parsing arguments with basic usage  """
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


def run_with_file_error(monkeypatch, error):
    """ Run parse_arguments with file-related error  """
    sys.argv = ["yt-dl-cli"]
    from pathlib import Path

    monkeypatch.setattr(
        Path, "read_text", lambda self, encoding=None: (_ for _ in ()).throw(error)
    )

    stderr = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = stderr

    config = parse_arguments()  # должен обработать ошибку, вернуть config с пустым urls

    sys.stderr = old_stderr

    return config, stderr.getvalue()


def test_parse_arguments_filenotfound(monkeypatch):
    """ Test parsing arguments with FileNotFoundError  """
    config, output = run_with_file_error(monkeypatch, FileNotFoundError("test"))
    assert config.urls == []
    assert "not found" in output or "Error" in output


def test_parse_arguments_permissionerror(monkeypatch):
    """ Test parsing arguments with PermissionError  """
    config, output = run_with_file_error(monkeypatch, PermissionError("test"))
    assert config.urls == []
    assert "Permission denied" in output or "Error" in output


def test_parse_arguments_unicodeerror(monkeypatch):
    """ Test parsing arguments with UnicodeDecodeError  """
    config, output = run_with_file_error(
        monkeypatch, UnicodeDecodeError("utf-8", b"", 0, 1, "reason")
    )
    assert config.urls == []
    assert "Encoding error" in output or "Error" in output


def test_parse_arguments_generic_exception(monkeypatch):
    """ Test parsing arguments with generic exception  """
    config, output = run_with_file_error(monkeypatch, Exception("Some error"))
    assert config.urls == []
    assert "Error" in output


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
        (Exception, ("Some error",), "Error reading"),  # generic fallback
    ],
)
def test_parse_arguments_all_exceptions(monkeypatch, exc_type, exc_args, expected_part):
    """ Test parsing arguments with a variety of exceptions  """
    sys.argv = ["yt-dl-cli", "--file", "bad.txt"]

    # Patch Path.read_text to raise the desired exception
    def raise_exc(*a, **kw):
        raise exc_type(*exc_args)

    monkeypatch.setattr(Path, "read_text", raise_exc)

    printed = {}

    def fake_print(*args, file=None, **kwargs):
        # Capture all printed messages for later assertion
        printed["msg"] = args[0] if args else ""
        printed["file"] = file

    monkeypatch.setattr("builtins.print", fake_print)

    config = parse_arguments()
    assert config.urls == []  # Должен вернуть пустой список

    assert (
        expected_part in printed["msg"]
        or Messages.CLI.FILE_NOT_FOUND(file="bad.txt") in printed["msg"]
    )
    assert printed["file"] == sys.stderr
