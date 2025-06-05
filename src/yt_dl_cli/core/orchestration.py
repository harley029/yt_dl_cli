import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import time
from typing import Optional

from yt_dl_cli.config.config import Config
from yt_dl_cli.core.core import DownloadExecutor, DownloaderCore, VideoInfoExtractor
from yt_dl_cli.i18n.messages import Messages
from yt_dl_cli.utils.logger import LoggerFactory
from yt_dl_cli.utils.stats_manager import StatsManager
from yt_dl_cli.interfaces.strategies import get_strategy
from yt_dl_cli.utils.utils import FileSystemChecker


class AsyncOrchestrator:
    """
    Manages asynchronous execution of multiple downloads with concurrency control.

    This class handles the coordination of multiple concurrent downloads using
    asyncio and ThreadPoolExecutor, providing efficient parallel processing
    while respecting the configured worker limits.
    """

    def __init__(self, core: DownloaderCore, config: Config):
        """
        Initialize the async orchestrator with core downloader and configuration.

        Args:
            core (DownloaderCore): The core downloader instance to use for each download
            config (Config): Configuration containing URLs and concurrency settings
        """
        self.core = core
        self.config = config

    async def run(self) -> None:
        """
        Execute all configured downloads asynchronously with timing and reporting.

        This method:
        1. Validates that there are URLs to download
        2. Creates a thread pool with the configured number of workers
        3. Submits all download tasks to the thread pool
        4. Waits for all downloads to complete
        5. Generates and logs a final statistics report

        The method uses asyncio.gather() to wait for all downloads to complete,
        ensuring that statistics are only reported after all work is done.

        Note:
            Downloads run in threads to avoid blocking the asyncio event loop,
            since yt-dlp operations are CPU and I/O intensive.
        """
        if not self.config.urls:
            self.core.logger.warning(Messages.Orchestrator.NO_URLS())
            return

        self.core.logger.info(
            Messages.Orchestrator.STARTING(
                count=len(self.config.urls), workers=self.config.max_workers
            )
        )
        start = time.time()
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as pool:
            tasks = [
                loop.run_in_executor(pool, self.core.download_single, url)
                for url in self.config.urls
            ]
            await asyncio.gather(*tasks)

        elapsed = time.time() - start
        self.core.stats.report(self.core.logger, elapsed)


# -------------------- Dependency Injection Container --------------------
class DIContainer:
    """
    Dependency injection container for creating fully configured downloader instances.

    This class acts as a factory and dependency injection container, creating
    all the required components and wiring them together to produce a ready-to-use
    downloader core with all dependencies properly injected.
    """

    @staticmethod
    def create_downloader_core(
        config: Config, logger: Optional[logging.Logger] = None
    ) -> DownloaderCore:
        """
        Create a fully configured DownloaderCore with all dependencies injected.

        This factory method creates and wires together all the components needed
        for a functioning downloader:
        - Logger configured for the save directory
        - Format strategy based on configuration (audio/video)
        - Statistics manager for tracking results
        - File system checker for existence tests
        - Video info extractor for metadata
        - Download executor for actual downloads

        Args:
            config (Config): Application configuration to use for component setup

        Returns:
            DownloaderCore: Fully configured and ready-to-use downloader instance

        Note:
            This method implements the composition root pattern, centralizing
            all dependency creation and injection in one place.
        """
        logger = logger or LoggerFactory.get_logger(config.save_dir)
        strategy = get_strategy(config)
        stats = StatsManager()
        file_checker = FileSystemChecker()
        info_extractor = VideoInfoExtractor(logger)
        download_executor = DownloadExecutor(logger)
        return DownloaderCore(
            config=config,
            strategy=strategy,
            stats=stats,
            logger=logger,
            file_checker=file_checker,
            info_extractor=info_extractor,
            download_executor=download_executor,
        )
