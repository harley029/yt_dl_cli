import argparse
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from yt_dl_cli.utils.validators import ArgValidator


@pytest.mark.parametrize(
    "is_file_return, stat_size, expected_exception, expected_msg",
    [
        (False, 10, argparse.ArgumentTypeError, "does not exist or is not a file"),
        (True, 0, argparse.ArgumentTypeError, "is empty"),
        (True, 10, None, ""),  # успешный кейс без исключений
    ],
)
def test_validate_url_file(is_file_return, stat_size, expected_exception, expected_msg):
    with patch.object(Path, "is_file", return_value=is_file_return), patch.object(
        Path, "stat", return_value=MagicMock(st_size=stat_size)
    ):

        if expected_exception:
            with pytest.raises(expected_exception) as excinfo:
                ArgValidator.validate_url_file("test.txt")
            assert expected_msg in str(excinfo.value)
        else:
            result = ArgValidator.validate_url_file("test.txt")
            assert isinstance(result, Path)


@pytest.mark.parametrize(
    "workers, should_raise",
    [("1", False), ("10", False), ("0", True), ("11", True), ("abc", True)],
)
def test_validate_workers(workers, should_raise):
    if should_raise:
        with pytest.raises(argparse.ArgumentTypeError):
            ArgValidator.validate_workers(workers)
    else:
        assert ArgValidator.validate_workers(workers) == int(workers)


@pytest.mark.parametrize(
    "quality, should_raise",
    [("best", False), ("720", False), ("999", True), ("low", True)],
)
def test_validate_quality(quality, should_raise):
    if should_raise:
        with pytest.raises(argparse.ArgumentTypeError):
            ArgValidator.validate_quality(quality)
    else:
        assert ArgValidator.validate_quality(quality) == quality
