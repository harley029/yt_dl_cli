import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from yt_dl_cli.utils.utils import FilenameSanitizer, FileSystemChecker


def test_filename_sanitizer():
    """ Testing of FilenameSanitizer.sanitize  """
    bad = "Bad/File:Name*With|Chars?"
    clean = FilenameSanitizer.sanitize(bad)
    assert "/" not in clean
    assert ":" not in clean
    assert "*" not in clean
    assert "|" not in clean
    assert "?" not in clean
    assert len(clean) <= 100


def test_filesystem_checker(tmp_path):
    """ Testing of FileSystemChecker  """
    # tmp_path — это стандартная pytest-фикстура для временной директории
    checker = FileSystemChecker()

    # Проверяем, что файл не существует
    test_file = tmp_path / "testfile.txt"
    assert not checker.exists(test_file)

    # Создаем файл
    test_file.write_text("hello")
    assert checker.exists(test_file)

    # Проверяем директорию
    assert checker.is_dir(tmp_path)
    assert not checker.is_dir(test_file)

    # Проверяем создание директории
    new_dir = tmp_path / "new_dir"
    assert not new_dir.exists()
    checker.ensure_dir(new_dir)
    assert new_dir.exists() and new_dir.is_dir()


def test_filename_sanitizer_type_error():
    """ Testing of FilenameSanitizer  with type and value errors  """
    # TypeError, если имя не строка
    with pytest.raises(TypeError):
        FilenameSanitizer.sanitize(12345)  # type: ignore


def test_filename_sanitizer_value_error():
    """ Testing of FilenameSanitizer  with value errors  """
    # ValueError, если max_length меньше 1
    with pytest.raises(ValueError):
        FilenameSanitizer.sanitize("goodname", max_length=0)
