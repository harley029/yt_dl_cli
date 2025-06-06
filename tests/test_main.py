import pytest
import sys

from yt_dl_cli.main import VideoDownloader


class DummyCore:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    @property
    def logger(self):
        class L:
            def warning(self, *args, **kwargs):
                self.last = args

            def critical(self, *args, **kwargs):
                self.last = args

        return L()


class DummyOrchestrator:
    def __init__(self, *a, **k):
        pass

    async def run(self):
        return None


@pytest.mark.filterwarnings("ignore:coroutine.*was never awaited")
def test_download_keyboard_interrupt(monkeypatch):
    # Мокаем DIContainer и orchestrator
    from yt_dl_cli import main

    monkeypatch.setattr(
        main.DIContainer, "create_downloader_core", lambda *a, **kw: DummyCore()
    )
    monkeypatch.setattr(
        main, "AsyncOrchestrator", lambda *a, **kw: DummyOrchestrator(*a, **kw)
    )

    # Подменим asyncio.run чтобы выбрасывал KeyboardInterrupt
    monkeypatch.setattr(
        main.asyncio, "run", lambda coro: (_ for _ in ()).throw(KeyboardInterrupt())
    )

    d = VideoDownloader()
    # Просто убеждаемся что KeyboardInterrupt не приводит к падению
    # (у тебя по коду - он ловится и логгируется, программа не падает)
    d.download()


@pytest.mark.filterwarnings("ignore:coroutine.*was never awaited")
def test_download_system_exit(monkeypatch):
    from yt_dl_cli import main

    monkeypatch.setattr(
        main.DIContainer, "create_downloader_core", lambda *a, **kw: DummyCore()
    )
    monkeypatch.setattr(
        main, "AsyncOrchestrator", lambda *a, **kw: DummyOrchestrator(*a, **kw)
    )
    # sys.exit вызывает SystemExit
    monkeypatch.setattr(
        main.asyncio, "run", lambda coro: (_ for _ in ()).throw(SystemExit(5))
    )
    d = VideoDownloader()
    with pytest.raises(SystemExit) as excinfo:
        d.download()
    assert excinfo.value.code == 5


@pytest.mark.filterwarnings("ignore:coroutine.*was never awaited")
def test_download_generic_exception(monkeypatch):
    from yt_dl_cli import main

    logs = []

    class DummyLogger:
        def warning(self, msg):
            logs.append(("warn", msg))

        def critical(self, msg):
            logs.append(("crit", msg))

    class DummyCoreWithLogger(DummyCore):
        @property
        def logger(self):
            return DummyLogger()

    monkeypatch.setattr(
        main.DIContainer,
        "create_downloader_core",
        lambda *a, **kw: DummyCoreWithLogger(),
    )
    monkeypatch.setattr(
        main, "AsyncOrchestrator", lambda *a, **kw: DummyOrchestrator(*a, **kw)
    )
    monkeypatch.setattr(
        main.asyncio, "run", lambda coro: (_ for _ in ()).throw(Exception("TestError"))
    )
    # Мокаем sys.exit чтобы не завершить pytest!
    monkeypatch.setattr(
        sys, "exit", lambda code=1: (_ for _ in ()).throw(SystemExit(code))
    )
    d = VideoDownloader()
    with pytest.raises(SystemExit) as excinfo:
        d.download()
    # Проверяем что логи записались
    assert any("crit" in l for l in logs)


@pytest.mark.filterwarnings("ignore:coroutine.*was never awaited")
def test_main_video_downloader_download(monkeypatch):
    from yt_dl_cli import main

    class DummyCore:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return False

        @property
        def logger(self):
            class L:
                def warning(self, *a, **k):
                    pass

                def critical(self, *a, **k):
                    pass

            return L()

    # --- Ключевой момент: возвращаем корутину!
    async def dummy_run():
        return None

    class DummyOrchestratorAsync(DummyOrchestrator):
        async def run(self):  # noqa
            return await dummy_run()

    monkeypatch.setattr(
        main.DIContainer, "create_downloader_core", lambda *a, **k: DummyCore()
    )
    monkeypatch.setattr(
        main, "AsyncOrchestrator", lambda *a, **k: DummyOrchestratorAsync(*a, **k)
    )
    # Можно оставить так (настоящий asyncio.run), потому что run теперь awaitable
    downloader = main.VideoDownloader()
    downloader.download()


@pytest.mark.filterwarnings("ignore:coroutine.*was never awaited")
def test_main_main_function_invokes_download(monkeypatch):
    """Проверяет, что main.main() создает VideoDownloader и вызывает download()."""
    from yt_dl_cli import main

    called = {}

    class DummyDownloader:
        def __init__(self):
            called["init"] = True

        def download(self):
            called["download"] = True

    # Мокаем VideoDownloader внутри main.py
    monkeypatch.setattr(main, "VideoDownloader", DummyDownloader)

    main.main()
    assert called.get("init")
    assert called.get("download")
