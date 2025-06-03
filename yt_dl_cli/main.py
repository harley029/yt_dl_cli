import asyncio
import logging
from typing import Optional

from src.config.config import Config
from src.utils.logger import LoggerFactory
from src.core.orchestration import AsyncOrchestrator, DIContainer
from src.utils.parser import parse_arguments

# -------------------- Internationalization --------------------
from src.i18n.init import setup_i18n

setup_i18n()  # noqa: E402
from src.i18n.messages import Messages  # noqa: E402


class VideoDownloader:
    """
    Main class that orchestrates the entire download process.

    This class serves as the main entry point for the application. It:
    1. Parses command line arguments to create configuration
    2. Uses dependency injection to create a configured downloader
    3. Creates an async orchestrator to manage concurrent downloads
    4. Runs the download process with proper error handling
    5. Handles user interruption (Ctrl+C) and critical errors gracefully

    Error Handling:
        - KeyboardInterrupt: Logs a warning about user interruption
        - General Exception: Logs critical errors with full exception details

    Note:
        This class is designed to be called from __main__ and handles
        all top-level error conditions to prevent crashes and provide
        meaningful error messages to users.

    Example usage:
        >>> downloader = VideoDownloader()
        >>> downloader.download()
    """

    def __init__(
        self, config: Optional[Config] = None, logger: Optional[logging.Logger] = None
    ):
        self.config = config or parse_arguments()
        self.logger = logger or LoggerFactory.get_logger(self.config.save_dir)

    def download(self) -> None:
        core = DIContainer.create_downloader_core(self.config, logger=self.logger)
        orchestrator = AsyncOrchestrator(core, self.config)
        try:
            with core:
                asyncio.run(orchestrator.run())
        except KeyboardInterrupt:
            core.logger.warning(Messages.CLI.USER_INTERRUPT)
        except Exception as e:
            core.logger.critical(Messages.CLI.CRITICAL_ERROR.format(error=e))


if __name__ == "__main__":
    downloader = VideoDownloader()
    downloader.download()
