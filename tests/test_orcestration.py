import asyncio

from yt_dl_cli.core.orchestration import AsyncOrchestrator


class DummyLogger:
    def __init__(self):
        self.calls = []

    def warning(self, msg):
        self.calls.append(("warning", msg))

    def info(self, msg):
        self.calls.append(("info", msg))


class DummyStats:
    def report(self, logger, elapsed):
        pass


class DummyCore:
    def __init__(self):
        self.logger = DummyLogger()
        self.stats = DummyStats()

    def download_single(self, url):
        pass


class DummyConfig:
    def __init__(self):
        self.urls = []
        self.max_workers = 2


def test_async_orchestrator_no_urls(monkeypatch):
    from yt_dl_cli.i18n.messages import Messages

    core = DummyCore()
    config = DummyConfig()
    orchestrator = AsyncOrchestrator(core, config)  # type: ignore
    # Проверяем что run() возвращается сразу и вызывает warning
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(orchestrator.run())
    finally:
        loop.close()
    assert ("warning", Messages.Orchestrator.NO_URLS()) in core.logger.calls
