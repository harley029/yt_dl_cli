import sys
import types
import pytest


def test_cli_importerror(monkeypatch):
    """Искусственно проверяет ImportError при импорте VideoDownloader."""

    # Создаём поддельный модуль yt_dl_cli.main, который выбрасывает ImportError при импорте
    sys.modules.pop("yt_dl_cli.main", None)

    def fake_import(*args, **kwargs):
        raise ImportError("Test import error")

    monkeypatch.setitem(
        sys.modules, "yt_dl_cli.main", types.ModuleType("yt_dl_cli.main")
    )
    monkeypatch.setattr(
        "yt_dl_cli.main.VideoDownloader", property(fake_import), raising=False
    )

    # Удаляем cli.py из sys.modules, чтобы при импорте он заново выполнился
    sys.modules.pop("yt_dl_cli.scripts.cli", None)

    with pytest.raises(ImportError):
        # Импортируем cli — он попытается импортировать VideoDownloader, что вызовет ImportError
        import yt_dl_cli.scripts.cli

        # Для надежности можно явно вызвать reload:
        import importlib

        importlib.reload(yt_dl_cli.scripts.cli)


def test_cli_handles_systemexit(monkeypatch):
    """Проверяет, что main() корректно выбрасывает SystemExit, если download вызывает sys.exit()."""
    from yt_dl_cli.scripts import cli

    class DummyDownloader:
        def download(self):
            sys.exit(2)  # Эмулируем критическую ошибку

    monkeypatch.setattr(cli, "VideoDownloader", lambda: DummyDownloader())

    with pytest.raises(SystemExit) as excinfo:
        cli.main()
    assert excinfo.value.code == 2
