import sys
from yt_dl_cli.config.config import Config


def test_config_parsing_from_args():
    """
    Проверяет, что аргументы командной строки корректно парсятся в объект Config.
    """
    # Имитируем аргументы командной строки
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

    # Подменяем sys.argv, чтобы Config их использовал
    original_argv = sys.argv
    sys.argv = test_args

    config = Config()

    # Восстанавливаем оригинальные аргументы
    sys.argv = original_argv

    assert config.urls == ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
    assert config.save_dir == "test_videos"
    assert config.quality == "720"
    assert config.max_workers == 5
    assert config.audio_only is True


def test_config_default_values():
    """
    Проверяет, что значения по умолчанию устанавливаются правильно, если аргументы не переданы.
    """
    original_argv = sys.argv
    sys.argv = ["yt-dl-cli"]  # Запускаем без аргументов

    config = Config()

    sys.argv = original_argv

    assert config.urls == []
    assert config.save_dir == "."  # Значение по умолчанию
    assert config.quality == "best"
    assert config.max_workers == 4
    assert config.audio_only is False
