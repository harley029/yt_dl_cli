# pylint: disable=too-many-instance-attributes, too-many-arguments, too-many-positional-arguments
# pylint: disable=broad-exception-caught


from typing import Any, Dict

import yt_dlp  # type: ignore

from yt_dl_cli.i18n.messages import Messages
from yt_dl_cli.interfaces.interfaces import IFileChecker, ILogger, IStatsCollector
from yt_dl_cli.interfaces.strategies import IFormatStrategy
from yt_dl_cli.utils.utils import FilenameSanitizer
from yt_dl_cli.config.config import Config


class VideoInfoExtractor:
    """
    Handles extraction of video metadata without downloading content.

    This class wraps yt-dlp's info extraction capabilities, providing
    error handling and logging for metadata retrieval operations.
    """

    def __init__(self, logger: ILogger):
        """
        Initialize the video info extractor with a logger.

        Args:
            logger (ILogger): Logger instance for error reporting
        """
        self.logger = logger

    def extract_info(self, url: str, opts: Dict[str, Any]) -> Any:
        """
        Extract video information from a URL without downloading.

        Uses yt-dlp to retrieve metadata about a video including title,
        duration, available formats, etc. This is used to check if a
        video exists and get its title before attempting download.

        Args:
            url (str): Video URL to extract information from
            opts (Dict[str, Any]): yt-dlp options for the extraction

        Returns:
            Any: Video information dictionary from yt-dlp, or None if extraction failed

        Note:
            Errors are logged but not raised, allowing the calling code to
            handle None return values gracefully.
        """
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise yt_dlp.DownloadError(Messages.Extractor.ERROR_NO_INFO())
                return info
        except yt_dlp.DownloadError as e:
            self.logger.error(Messages.Extractor.ERROR_EXTRACT(url=url, error=e))
            return None
        except yt_dlp.utils.ExtractorError as e:
            self.logger.error(Messages.Extractor.ERROR_EXTRACT(url=url, error=e))
            return None
        except Exception as e:
            self.logger.error(Messages.Extractor.ERROR_EXTRACT(url=url, error=e))
            return None


class DownloadExecutor:
    """
    Handles the actual download execution using yt-dlp.

    This class wraps yt-dlp's download functionality with error handling
    and logging, providing a clean interface for download operations.
    """

    def __init__(self, logger: ILogger):
        """
        Initialize the download executor with a logger.

        Args:
            logger (ILogger): Logger instance for error reporting
        """
        self.logger = logger

    def execute_download(self, url: str, opts: Dict[str, Any]) -> bool:
        """
        Execute a download operation for a single URL.

        Performs the actual download using yt-dlp with the provided options,
        handling any errors that occur during the download process.

        Args:
            url (str): Video URL to download
            opts (Dict[str, Any]): yt-dlp configuration options

        Returns:
            bool: True if download succeeded, False if it failed

        Note:
            All exceptions are caught and logged, ensuring that one failed
            download doesn't crash the entire application.
        """
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
                return True
        except yt_dlp.DownloadError as e:
            self.logger.error(Messages.Executor.ERROR_DOWNLOAD(url=url, error=e))
            return False
        except Exception as e:
            self.logger.error(Messages.Executor.ERROR_DOWNLOAD(url=url, error=e))
            return False


# -------------------- Core Downloader --------------------
class DownloaderCore:
    """
    Core download logic coordinator that orchestrates the download process.

    This class brings together all the components needed for downloading:
    configuration, format strategies, statistics, file checking, and the
    actual download execution. It handles the complete workflow for a
    single download operation.
    """

    def __init__(
        self,
        config: Config,
        strategy: IFormatStrategy,
        stats: IStatsCollector,
        logger: ILogger,
        file_checker: IFileChecker,
        info_extractor: VideoInfoExtractor,
        download_executor: DownloadExecutor,
    ):
        """
        Initialize the downloader core with all required dependencies.

        Args:
            config (Config): Application configuration
            strategy (IFormatStrategy): Format selection strategy (video/audio)
            stats (StatsManager): Statistics tracking manager
            logger (ILogger): Logger for output and error reporting
            file_checker (FileSystemChecker): File system operations
            info_extractor (VideoInfoExtractor): Video metadata extraction
            download_executor (DownloadExecutor): Actual download execution
        """
        self.config = config
        self.strategy = strategy
        self.stats = stats
        self.logger = logger
        self.file_checker = file_checker
        self.info_extractor = info_extractor
        self.download_executor = download_executor
        self._resources: list[Any] = []

    def __enter__(self):
        """
        Context manager entry point for resource management.

        Returns:
            DownloaderCore: Self reference for use in with statements
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point for resource cleanup.

        Ensures all registered resources are properly closed when the
        downloader core goes out of scope or the with block ends.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        for resource in self._resources:
            try:
                if hasattr(resource, "close"):
                    resource.close()
            except Exception as e:
                self.logger.warning(Messages.Core.ERROR_RESOURCE_CLOSE(error=e))

    def register_resource(self, resource):
        """
        Register a resource for automatic cleanup.

        Args:
            resource: Any object with a close() method that needs cleanup
        """
        self._resources.append(resource)

    def download_single(self, url: str) -> None:
        """
        Download a single video from the provided URL.

        This method orchestrates the complete download process for a single URL:
        1. Extract video information to get title and check availability
        2. Create sanitized filename and check if file already exists
        3. Skip download if file exists, otherwise proceed with download
        4. Update statistics based on the outcome

        Args:
            url (str): Video URL to download

        Note:
            This method handles all error conditions gracefully and updates
            statistics appropriately. It's designed to be called concurrently
            for multiple URLs.
        """
        base_opts = self.strategy.get_opts()
        base_opts.update({"ignoreerrors": True, "no_warnings": False})
        info = self.info_extractor.extract_info(url, base_opts)
        if info is None:
            self.stats.record_failure()
            return

        title = info.get("title", "Unknown")
        sanitized = FilenameSanitizer.sanitize(title)
        ext = "mp3" if self.config.audio_only else "mp4"
        filepath = self.config.save_dir / f"{sanitized}.{ext}"

        if self.file_checker.exists(filepath):
            self.logger.info(Messages.Core.SKIP_EXISTS(title=title))
            self.stats.record_skip()
            return

        opts = base_opts.copy()
        opts["outtmpl"] = str(self.config.save_dir / f"{sanitized}.%(ext)s")

        self.logger.info(Messages.Core.START_DOWNLOAD(title=title))
        if self.download_executor.execute_download(url, opts):
            self.stats.record_success()
            self.logger.info(Messages.Core.DONE_DOWNLOAD(title=title))
        else:
            self.stats.record_failure()
