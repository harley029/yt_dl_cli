import asyncio

from yt_dl_cli.core.orchestration import AsyncOrchestrator


class DummyLogger:
    """Logger for tests"""
    def __init__(self):
        """init Logger for tests"""
        self.calls = []

    def warning(self, msg):
        """Log warning messages"""
        self.calls.append(("warning", msg))

    def info(self, msg):
        """Log info messages"""
        self.calls.append(("info", msg))


class DummyStats:
    """Stats for tests"""
    def report(self, logger, elapsed):
        """Report stats"""


class DummyCore:
    """Core for tests"""
    def __init__(self):
        """Init Core for tests"""
        self.logger = DummyLogger()
        self.stats = DummyStats()

    def download_single(self, url):
        """Download single video"""


class DummyConfig:
    """Config for tests"""
    def __init__(self):
        """Init Config for tests"""
        self.urls = []
        self.max_workers = 2


def test_async_orchestrator_no_urls(monkeypatch):
    """Test AsyncOrchestrator with no URLs"""
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
