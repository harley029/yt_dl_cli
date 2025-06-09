"""
Asynchronous Download Orchestration Module

This module provides the main orchestration layer for managing concurrent video downloads.
It contains the AsyncOrchestrator class for coordinating multiple downloads and the
DIContainer class for dependency injection and component creation.

The module implements asynchronous processing using asyncio and ThreadPoolExecutor
to efficiently handle multiple downloads while respecting concurrency limits and
providing comprehensive statistics reporting.

Classes:
    AsyncOrchestrator: Main orchestrator for managing concurrent downloads
    DIContainer: Dependency injection container for component creation

Key Features:
    - Asynchronous download coordination with configurable concurrency
    - Thread-based execution to avoid blocking the event loop
    - Comprehensive timing and statistics reporting
    - Dependency injection pattern for clean component composition
    - Proper resource management with context managers

Dependencies:
    - asyncio: For asynchronous execution and event loop management
    - concurrent.futures: For thread pool execution
    - logging: For logger type hints and configuration
    - time: For performance timing measurements
    - typing: For type hints and annotations
    - Various yt_dl_cli modules: For core functionality and configuration
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from typing import Optional

from yt_dl_cli.config.config import Config
from yt_dl_cli.core.core import DownloadExecutor, DownloaderCore, VideoInfoExtractor
from yt_dl_cli.i18n.messages import Messages
from yt_dl_cli.interfaces.interfaces import ILogger
from yt_dl_cli.utils.logger import LoggerFactory
from yt_dl_cli.utils.stats_manager import StatsManager
from yt_dl_cli.interfaces.strategies import get_strategy
from yt_dl_cli.utils.utils import FileSystemChecker


class AsyncOrchestrator:
    """
    Manages asynchronous execution of multiple downloads with concurrency control.

    This class handles the coordination of multiple concurrent downloads using
    asyncio and ThreadPoolExecutor, providing efficient parallel processing
    while respecting the configured worker limits. It serves as the main
    orchestration layer for the download application.

    The orchestrator manages the entire download lifecycle from initialization
    through completion, including timing measurements and final reporting.

    Attributes:
        core (DownloaderCore): The core downloader instance used for each download
        config (Config): Configuration containing URLs and concurrency settings

    Example:
        >>> import asyncio
        >>> from yt_dl_cli.config.config import Config
        >>> from pathlib import Path
        >>>
        >>> config = Config(
        ...     save_dir=Path("/downloads"),
        ...     max_workers=4,
        ...     quality="720",
        ...     audio_only=False,
        ...     urls=["https://example.com/video1", "https://example.com/video2"]
        ... )
        >>> core = DIContainer.create_downloader_core(config)
        >>> orchestrator = AsyncOrchestrator(core, config)
        >>> asyncio.run(orchestrator.run())
    """

    def __init__(self, core: DownloaderCore, config: Config) -> None:
        """
        Initialize the async orchestrator with core downloader and configuration.

        Sets up the orchestrator with the necessary components for managing
        concurrent downloads. The core downloader and configuration are stored
        as instance attributes for use during execution.

        Args:
            core (DownloaderCore): The core downloader instance to use for each download.
                                 Must be fully configured with all dependencies.
            config (Config): Configuration containing URLs and concurrency settings.
                           Must include valid URLs list and max_workers setting.

        Example:
            >>> core = DIContainer.create_downloader_core(config)
            >>> orchestrator = AsyncOrchestrator(core, config)
        """
        self.core = core
        self.config = config

    async def run(self) -> None:
        """
        Execute all configured downloads asynchronously with timing and reporting.

        This method orchestrates the complete download process:
        1. Validates that there are URLs to download
        2. Logs the start of operations with worker and URL counts
        3. Creates a thread pool with the configured number of workers
        4. Submits all download tasks to the thread pool using run_in_executor
        5. Waits for all downloads to complete using asyncio.gather
        6. Measures total elapsed time and generates final statistics report

        The method uses asyncio.gather() to wait for all downloads to complete,
        ensuring that statistics are only reported after all work is done.
        Downloads run in threads to avoid blocking the asyncio event loop,
        since yt-dlp operations are CPU and I/O intensive.

        Raises:
            Exception: Any exception from individual downloads will be propagated
                      after other downloads complete (due to asyncio.gather behavior).

        Note:
            If no URLs are configured, the method logs a warning and returns early
            without performing any downloads.

        Example:
            >>> orchestrator = AsyncOrchestrator(core, config)
            >>> await orchestrator.run()
            # Logs: "Starting download of 5 URLs with 4 workers"
            # ... downloads execute concurrently ...
            # Logs: Final statistics report with timing information
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

    This class acts as a factory and dependency injection container, implementing
    the composition root pattern. It creates all the required components and wires
    them together to produce a ready-to-use downloader core with all dependencies
    properly injected.

    The container centralizes dependency creation and management, making the system
    more testable and maintainable by removing direct dependencies between components.

    Static Methods:
        create_downloader_core: Factory method for creating configured DownloaderCore instances

    Design Pattern:
        This class implements the Dependency Injection Container pattern and
        Composition Root pattern, providing a single place where all object
        composition happens.
    """

    @staticmethod
    def create_downloader_core(
        config: Config, logger: Optional[ILogger] = None
    ) -> DownloaderCore:
        """
        Create a fully configured DownloaderCore with all dependencies injected.

        This factory method creates and wires together all the components needed
        for a functioning downloader system. It handles the complete object graph
        construction, ensuring all components are properly configured and connected.

        Components created and wired:
        - Logger: Configured for the specified save directory
        - Format strategy: Selected based on audio_only configuration
        - Statistics manager: For tracking download results
        - File system checker: For file existence validation
        - Video info extractor: For metadata retrieval
        - Download executor: For actual download operations
        - DownloaderCore: Main coordinator with all dependencies injected

        Args:
            config (Config): Application configuration to use for component setup.
                           Must contain valid save_dir, quality, audio_only settings.
            logger (Optional[logging.Logger], optional): Custom logger instance.
                                                       If None, creates a new logger
                                                       using LoggerFactory. Defaults to None.

        Returns:
            DownloaderCore: Fully configured and ready-to-use downloader instance
                          with all dependencies properly injected and initialized.

        Example:
            >>> from pathlib import Path
            >>> config = Config(
            ...     save_dir=Path("/downloads"),
            ...     max_workers=4,
            ...     quality="720",
            ...     audio_only=False
            ... )
            >>> core = DIContainer.create_downloader_core(config)
            >>> # core is now ready to use with all dependencies configured

        Note:
            This method implements the composition root pattern, centralizing
            all dependency creation and injection in one place. This makes the
            system more testable and maintainable by providing a single point
            of object graph construction.
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
