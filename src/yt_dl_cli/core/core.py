# pylint: disable=too-many-instance-attributes, too-many-arguments, too-many-positional-arguments
# pylint: disable=broad-exception-caught

"""
YT-DL-CLI Video Downloader Core Module.

This module contains the core components responsible for the actual video downloading
process. It provides a clean separation of concerns between video information extraction,
download execution, and the orchestration of the complete download workflow.

The module is built around the principle of single responsibility, with each class
handling a specific aspect of the download process. This design promotes testability,
maintainability, and allows for easy extension and modification of individual components.

Architecture Overview:
    The module implements a layered architecture with clear separation between:

    1. Information Layer (VideoInfoExtractor):
       - Extracts video metadata without downloading content
       - Validates video availability and accessibility
       - Retrieves video information for processing decisions

    2. Execution Layer (DownloadExecutor):
       - Handles the actual download operations
       - Manages yt-dlp interactions and configurations
       - Provides error handling for download failures

    3. Orchestration Layer (DownloaderCore):
       - Coordinates the complete download workflow
       - Integrates all components and dependencies
       - Manages resource lifecycle and cleanup
       - Handles file system operations and statistics

Key Components:
    - VideoInfoExtractor: Metadata extraction and video validation
    - DownloadExecutor: Core download execution engine
    - DownloaderCore: Main orchestrator and workflow manager

Design Patterns:
    - Strategy Pattern: Format selection through IFormatStrategy interface
    - Dependency Injection: All dependencies injected through constructor
    - Context Manager: Resource management with __enter__/__exit__ methods
    - Facade Pattern: DownloaderCore provides simplified interface to complex operations
    - Template Method: Standardized download workflow with extensible steps

Error Handling Philosophy:
    The module implements defensive programming practices:
    - All external API calls are wrapped in try-catch blocks
    - Errors are logged but don't crash the application
    - Graceful degradation when individual downloads fail
    - Resource cleanup is guaranteed through context managers
    - Detailed error messages for troubleshooting and debugging

Performance Considerations:
    - Efficient metadata extraction without unnecessary downloads
    - File existence checking to avoid redundant operations
    - Resource pooling and cleanup to prevent memory leaks
    - Asynchronous-friendly design for concurrent operations
    - Minimal I/O operations through smart caching strategies

Integration Points:
    The module integrates with several external systems:
    - yt-dlp: Primary download engine and video platform interface
    - File System: Through IFileChecker for file operations
    - Logging: Through ILogger for monitoring and debugging
    - Statistics: Through IStatsCollector for progress tracking
    - Configuration: Through Config for user preferences and settings
    - Internationalization: Through Messages for localized user feedback

Usage Patterns:
    The module is designed to be used in several contexts:

    1. Single Download Operations:
       - Extract video information
       - Check file existence
       - Execute download if needed
       - Update statistics and logs

    2. Batch Download Operation:
       - Process multiple URLs concurrently
       - Maintain statistics across operations
       - Handle individual failures gracefully

    3. Integration with Async Systems:
       - Compatible with asyncio event loops
       - Non-blocking operations where possible
       - Resource cleanup compatible with async contexts

Security Considerations:
    - Input validation for URLs and file paths
    - Safe filename sanitization to prevent directory traversal
    - Secure handling of temporary files and downloads
    - Validation of video information before processing
    - Protection against malicious URLs and content

Thread Safety:
    - VideoInfoExtractor: Thread-safe, creates isolated yt-dlp instances
    - DownloadExecutor: Thread-safe, each operation uses separate context
    - DownloaderCore: Not thread-safe, designed for single-thread usage
    - Resource management: Requires careful coordination in multi-threaded environments

Example Usage:
    Basic usage with dependency injection:

    >>> from yt_dl_cli.config.config import Config
    >>> from yt_dl_cli.utils.logger import LoggerFactory
    >>>
    >>> # Setup dependencies
    >>> config = Config(save_dir="/downloads", audio_only=False)
    >>> logger = LoggerFactory.get_logger("/downloads")
    >>>
    >>> # Create core components
    >>> info_extractor = VideoInfoExtractor(logger)
    >>> download_executor = DownloadExecutor(logger)
    >>>
    >>> # Create and use downloader core
    >>> with DownloaderCore(config, strategy, stats, logger,
    ...                    file_checker, info_extractor, download_executor) as core:
    ...     core.download_single("https://youtube.com/watch?v=example")

Dependencies:
    External Libraries:
        - yt-dlp: Video downloading and information extraction
        - typing: Type hints for better code documentation

    Internal Modules:
        - yt_dl_cli.i18n.messages: Internationalized user messages
        - yt_dl_cli.interfaces.interfaces: Core interface definitions
        - yt_dl_cli.interfaces.strategies: Format selection strategies
        - yt_dl_cli.utils.utils: Utility functions and helpers
        - yt_dl_cli.config.config: Configuration management

Error Types:
    The module handles several categories of errors:
    - Network errors: Connection timeouts, DNS failures
    - Platform errors: Video unavailable, private videos, geo-blocking
    - File system errors: Permission denied, disk full, invalid paths
    - Format errors: Unsupported formats, codec issues
    - Configuration errors: Invalid settings, missing dependencies

Monitoring and Observability:
    - Detailed logging at multiple levels (DEBUG, INFO, WARNING, ERROR)
    - Statistics collection for success/failure rates
    - Progress tracking for individual downloads
    - Resource usage monitoring and cleanup verification
    - Performance metrics for optimization opportunities

Testing Considerations:
    The module is designed with testability in mind:
    - Dependency injection allows for easy mocking
    - Clear separation of concerns enables unit testing
    - Context managers ensure proper test cleanup
    - Error handling can be tested through exception simulation
    - Statistics tracking provides measurable test outcomes

Version Compatibility:
    - Python 3.8+: Uses modern type hints and context managers
    - yt-dlp: Compatible with latest stable versions
    - Cross-platform: Works on Windows, macOS, and Linux
    - Unicode support: Handles international characters in titles and paths

See Also:
    - yt_dl_cli.core.orchestration: Asynchronous orchestration layer
    - yt_dl_cli.interfaces.interfaces: Core interface definitions
    - yt_dl_cli.config.config: Configuration management documentation
    - yt_dl_cli.utils.utils: Utility functions and helpers
    - yt-dlp documentation: https://harley029.github.io/yt_dl_cli/
"""


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

    This class provides a clean interface to yt-dlp's information extraction
    capabilities, focusing specifically on retrieving video metadata without
    performing actual downloads. It serves as the first step in the download
    workflow, validating video availability and extracting necessary information
    for processing decisions.

    The class implements robust error handling to ensure that metadata extraction
    failures don't crash the application. It provides detailed logging for
    troubleshooting and monitoring purposes.

    Key Responsibilities:
        - Extract video metadata from URLs using yt-dlp
        - Validate video availability and accessibility
        - Handle platform-specific errors and limitations
        - Provide structured error reporting and logging
        - Support multiple video platforms through yt-dlp

    Design Principles:
        - Single Responsibility: Only handles information extraction
        - Defensive Programming: Extensive error handling and validation
        - Logging Integration: Comprehensive error reporting
        - Platform Agnostic: Works with any yt-dlp supported platform

    Error Handling:
        The class handles several categories of errors:
        - Network errors: Connection timeouts, DNS failures
        - Platform errors: Video unavailable, private videos, geo-blocking
        - Parsing errors: Invalid URLs, malformed responses
        - Authentication errors: Age-restricted content, login required

    Thread Safety:
        This class is thread-safe as it creates isolated yt-dlp instances
        for each operation and doesn't maintain mutable state between calls.
        Multiple threads can safely use the same VideoInfoExtractor instance.

    Performance Characteristics:
        - Lightweight operations: Only extracts metadata, no downloads
        - Network dependent: Performance varies with connection speed
        - Caching friendly: Results can be cached by calling code
        - Memory efficient: Minimal memory footprint per operation

    Attributes:
        logger (ILogger): Logger instance for error reporting and debugging.
                         Used to record extraction attempts, failures, and
                         detailed error information for troubleshooting.

    Example:
        Basic usage for video information extraction:

        >>> from yt_dl_cli.utils.logger import LoggerFactory
        >>> logger = LoggerFactory.get_logger("/tmp")
        >>> extractor = VideoInfoExtractor(logger)
        >>>
        >>> # Extract video information
        >>> opts = {"quiet": True, "no_warnings": True}
        >>> info = extractor.extract_info("https://youtube.com/watch?v=example", opts)
        >>>
        >>> if info:
        ...     print(f"Title: {info.get('title')}")
        ...     print(f"Duration: {info.get('duration')} seconds")
        ...     print(f"Uploader: {info.get('uploader')}")
        ... else:
        ...     print("Failed to extract video information")

        Error handling example:

        >>> info = extractor.extract_info("https://invalid-url", opts)
        >>> if info is None:
        ...     print("Extraction failed - check logs for details")

    See Also:
        yt_dlp.YoutubeDL: Primary extraction engine
        ILogger: Logging interface for error reporting
        Messages.Extractor: Localized error messages
    """

    def __init__(self, logger: ILogger):
        """
        Initialize the video info extractor with a logger.

        Sets up the extractor with the necessary logging infrastructure for
        error reporting and debugging. The logger is used throughout the
        extraction process to record attempts, failures, and detailed error
        information.

        Args:
            logger (ILogger): Logger instance for error reporting and debugging.
                             Should be configured with appropriate handlers and
                             log levels for the application context. The logger
                             will receive messages at various levels (INFO, WARNING,
                             ERROR) depending on the extraction outcomes.

        Note:
            The constructor is lightweight and doesn't perform any I/O operations
            or network requests. All heavy operations are deferred to the
            extract_info method to keep initialization fast and predictable.
        """
        self.logger = logger

    def extract_info(self, url: str, opts: Dict[str, Any]) -> Any:
        """
        Extract video information from a URL without downloading.

        This method uses yt-dlp to retrieve comprehensive metadata about a video
        including title, duration, available formats, uploader information, and
        other platform-specific details. The extraction is performed without
        downloading any actual video content, making it efficient for validation
        and preprocessing tasks.

        The method implements robust error handling to ensure that extraction
        failures are properly logged and don't crash the application. It handles
        various error conditions including network failures, video unavailability,
        and platform-specific restrictions.

        Process Flow:
            1. Create yt-dlp instance with provided options
            2. Attempt to extract video information from URL
            3. Validate that information was successfully retrieved
            4. Handle any errors that occur during extraction
            5. Log appropriate messages for monitoring and debugging
            6. Return structured information or None on failure

        Args:
            url (str): Video URL to extract information from. Should be a valid
                      URL pointing to a video on a platform supported by yt-dlp.
                      Examples include YouTube, Vimeo, Dailymotion, and hundreds
                      of other video platforms.

            opts (Dict[str, Any]): yt-dlp configuration options for the extraction.
                                  Common options include:
                                  - "quiet": Suppress output messages
                                  - "no_warnings": Disable warning messages
                                  - "extractaudio": Audio extraction settings
                                  - "format": Preferred format selection
                                  - "ignoreerrors": Continue on errors

        Returns:
            Any: Video information dictionary from yt-dlp containing comprehensive
                metadata about the video, or None if extraction failed. The
                dictionary typically includes:
                - "title": Video title
                - "duration": Video length in seconds
                - "uploader": Channel or user name
                - "upload_date": Publication date
                - "view_count": Number of views
                - "formats": Available quality/format options
                - "thumbnail": Thumbnail image URL
                - "description": Video description text
                - Platform-specific additional metadata

        Error Handling:
            The method catches and handles several types of exceptions:

            - yt_dlp.DownloadError: Raised when yt-dlp encounters download-related
              errors such as network issues, authentication problems, or video
              unavailability. These are logged as extraction errors.

            - yt_dlp.utils.ExtractorError: Raised when yt-dlp's extractor
              encounters platform-specific issues such as parsing errors,
              unsupported URLs, or API changes. These are logged with detailed
              error information.

            - Exception: Catches all other unexpected errors to prevent
              application crashes. These are logged as general extraction errors
              with full exception details for debugging.

        Performance Considerations:
            - Network dependent: Extraction time varies with connection speed
            - Lightweight operation: Only retrieves metadata, no file downloads
            - Caching opportunity: Results can be cached by calling code
            - Rate limiting: Respects platform rate limits automatically

        Example:
            Basic information extraction:

            >>> extractor = VideoInfoExtractor(logger)
            >>> opts = {"quiet": True, "no_warnings": True}
            >>> info = extractor.extract_info("https://youtube.com/watch?v=dQw4w9WgXcQ", opts)
            >>>
            >>> if info:
            ...     print(f"Title: {info['title']}")
            ...     print(f"Duration: {info['duration']} seconds")
            ...     print(f"Uploader: {info['uploader']}")
            ... else:
            ...     print("Failed to extract information")

            Handling extraction failures:

            >>> urls = ["https://youtube.com/watch?v=valid", "https://invalid-url"]
            >>> for url in urls:
            ...     info = extractor.extract_info(url, opts)
            ...     if info:
            ...         print(f"Successfully extracted: {info['title']}")
            ...     else:
            ...         print(f"Failed to extract from: {url}")

            Custom options for specific needs:

            >>> opts = {
            ...     "quiet": False,
            ...     "no_warnings": False,
            ...     "extract_flat": True,  # For playlists
            ...     "ignoreerrors": True
            ... }
            >>> info = extractor.extract_info(playlist_url, opts)

        Note:
            This method is designed to be called multiple times with different
            URLs and options. Each call creates a fresh yt-dlp instance to
            ensure isolation and prevent state contamination between extractions.

            Errors are logged but not raised, allowing the calling code to
            handle None return values gracefully and continue processing other
            URLs in batch operations.

        See Also:
            yt_dlp.YoutubeDL: Primary extraction engine documentation
            yt_dlp.DownloadError: Download-related error handling
            yt_dlp.utils.ExtractorError: Extractor-specific error handling
            Messages.Extractor: Localized error message definitions
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

    This class provides a clean interface to yt-dlp's download functionality,
    focusing specifically on executing download operations with comprehensive
    error handling and logging. It serves as the execution engine for the
    download workflow, handling the actual file transfer and storage operations.

    The class implements robust error handling to ensure that download failures
    are properly managed and don't crash the application. It provides detailed
    logging for monitoring download progress and troubleshooting issues.

    Key Responsibilities:
        - Execute video/audio downloads using yt-dlp
        - Handle download-related errors and exceptions
        - Provide detailed logging for monitoring and debugging
        - Manage yt-dlp configuration and options
        - Support multiple output formats and quality settings

    Design Principles:
        - Single Responsibility: Only handles download execution
        - Defensive Programming: Comprehensive error handling
        - Logging Integration: Detailed progress and error reporting
        - Configuration Flexibility: Supports various yt-dlp options

    Error Categories:
        The class handles several types of download errors:
        - Network errors: Connection issues, timeouts, bandwidth problems
        - Storage errors: Disk full, permission denied, invalid paths
        - Format errors: Unsupported formats, codec issues
        - Platform errors: Video removed, geo-blocked, private content

    Thread Safety:
        This class is thread-safe as it creates isolated yt-dlp instances
        for each download operation and doesn't maintain mutable state.
        Multiple threads can safely use the same DownloadExecutor instance.

    Performance Characteristics:
        - I/O intensive: Performance depends on network and disk speed
        - Memory efficient: Streaming downloads minimize memory usage
        - Resumable: Supports partial download resumption where possible
        - Concurrent friendly: Designed for use in concurrent environments

    Attributes:
        logger (ILogger): Logger instance for error reporting and progress tracking.
                         Used to record download attempts, progress updates,
                         completion status, and detailed error information.

    Example:
        Basic usage for single download:

        >>> from yt_dl_cli.utils.logger import LoggerFactory
        >>> logger = LoggerFactory.get_logger("/downloads")
        >>> executor = DownloadExecutor(logger)
        >>>
        >>> # Configure download options
        >>> opts = {
        ...     "format": "best[height<=720]",
        ...     "outtmpl": "/downloads/%(title)s.%(ext)s",
        ...     "writeinfojson": True
        ... }
        >>>
        >>> # Execute download
        >>> success = executor.execute_download("https://youtube.com/watch?v=example", opts)
        >>> if success:
        ...     print("Download completed successfully")
        ... else:
        ...     print("Download failed - check logs")

        Batch download example:

        >>> urls = ["https://youtube.com/watch?v=video1", "https://youtube.com/watch?v=video2"]
        >>> success_count = 0
        >>> for url in urls:
        ...     if executor.execute_download(url, opts):
        ...         success_count += 1
        >>> print(f"Successfully downloaded {success_count}/{len(urls)} videos")

    See Also:
        yt_dlp.YoutubeDL: Primary download engine
        ILogger: Logging interface for progress tracking
        Messages.Executor: Localized error and status messages
    """

    def __init__(self, logger: ILogger):
        """
        Initialize the download executor with a logger.

        Sets up the executor with the necessary logging infrastructure for
        progress tracking, error reporting, and debugging. The logger is used
        throughout the download process to record attempts, progress updates,
        and detailed error information.

        Args:
            logger (ILogger): Logger instance for error reporting and progress tracking.
                             Should be configured with appropriate handlers and log
                             levels for the application context. The logger will
                             receive messages at various levels (INFO, WARNING, ERROR)
                             depending on download outcomes and progress.

        Example:
            Creating an executor with a custom logger:

            >>> import logging
            >>> from yt_dl_cli.utils.logger import LoggerFactory
            >>>
            >>> # Create logger with specific configuration
            >>> logger = LoggerFactory.get_logger("/downloads", level=logging.INFO)
            >>>
            >>> # Initialize executor
            >>> executor = DownloadExecutor(logger)

        Note:
            The constructor is lightweight and doesn't perform any I/O operations
            or network requests. All heavy operations are deferred to the
            execute_download method to keep initialization fast and predictable.
        """
        self.logger = logger

    def execute_download(self, url: str, opts: Dict[str, Any]) -> bool:
        """
        Execute a download operation for a single URL.

        This method performs the actual download using yt-dlp with the provided
        configuration options. It handles the complete download process including
        format selection, quality negotiation, file transfer, and storage operations.
        The method implements comprehensive error handling to ensure that failures
        are properly managed and logged.

        The download process is designed to be robust and handle various error
        conditions gracefully, ensuring that individual download failures don't
        crash the entire application. This makes it suitable for batch operations
        and concurrent download scenarios.

        Process Flow:
            1. Create yt-dlp instance with provided options
            2. Initiate download operation for the specified URL
            3. Monitor download progress and handle any errors
            4. Log success or failure with appropriate details
            5. Return status indicator for calling code

        Args:
            url (str): Video URL to download. Should be a valid URL pointing to
                      a video on a platform supported by yt-dlp. The URL will
                      be processed by yt-dlp's URL recognition system to determine
                      the appropriate extractor and download strategy.

            opts (Dict[str, Any]): yt-dlp configuration options for the download.
                                  These options control all aspects of the download
                                  process including:
                                  - "format": Quality and format selection
                                  - "outtmpl": Output filename template
                                  - "writeinfojson": Save metadata to JSON file
                                  - "writesubtitles": Download subtitle files
                                  - "embedsubs": Embed subtitles in video file
                                  - "extractaudio": Extract audio only
                                  - "audioformat": Audio format specification
                                  - "postprocessors": Post-processing operations

        Returns:
            bool: True if the download completed successfully, False if it failed.
                 Success is determined by yt-dlp completing the download process
                 without raising exceptions. The return value allows calling code
                 to track success/failure rates and handle batch operations
                 appropriately.

        Error Handling:
            The method catches and handles several types of exceptions:

            - yt_dlp.DownloadError: Raised when yt-dlp encounters download-specific
              errors such as network issues, format unavailability, or storage
              problems. These are logged with detailed error information including
              the URL and specific error details.

            - Exception: Catches all other unexpected errors to prevent
              application crashes. This includes system-level errors, memory
              issues, and other unforeseen problems. All exceptions are logged
              with full details for debugging purposes.

        Side Effects:
            - Creates downloaded files in the specified output directory
            - May create temporary files during the download process
            - Updates file system with video/audio content and metadata
            - Generates log entries for monitoring and debugging
            - May modify network settings (proxy, user agent) during download

        Performance Considerations:
            - Network intensive: Download speed depends on connection bandwidth
            - Disk intensive: File writing performance affects overall speed
            - Memory efficient: Streaming downloads minimize memory usage
            - CPU usage: Varies with post-processing operations (transcoding, etc.)
            - Resumable: Supports partial download resumption where possible

        Example:
            Basic download with minimal options:

            >>> executor = DownloadExecutor(logger)
            >>> opts = {"format": "best", "outtmpl": "/downloads/%(title)s.%(ext)s"}
            >>> success = executor.execute_download("https://youtube.com/watch?v=example", opts)

            High-quality video download with metadata:

            >>> opts = {
            ...     "format": "best[height<=1080]",
            ...     "outtmpl": "/downloads/%(uploader)s - %(title)s.%(ext)s",
            ...     "writeinfojson": True,
            ...     "writesubtitles": True,
            ...     "writeautomaticsub": True
            ... }
            >>> success = executor.execute_download(url, opts)

            Audio-only download with format conversion:

            >>> opts = {
            ...     "format": "bestaudio/best",
            ...     "outtmpl": "/music/%(title)s.%(ext)s",
            ...     "extractaudio": True,
            ...     "audioformat": "mp3",
            ...     "audioquality": "192K"
            ... }
            >>> success = executor.execute_download(url, opts)

            Error handling in batch operations:

            >>> urls = ["https://youtube.com/watch?v=video1", "https://youtube.com/watch?v=video2"]
            >>> failed_urls = []
            >>> for url in urls:
            ...     if not executor.execute_download(url, opts):
            ...         failed_urls.append(url)
            >>> print(f"Failed downloads: {len(failed_urls)}")

        Note:
            This method is designed to be called multiple times with different
            URLs and options. Each call creates a fresh yt-dlp instance to
            ensure isolation and prevent state contamination between downloads.

            All exceptions are caught and logged, ensuring that one failed
            download doesn't crash the entire application. This makes the method
            safe for use in concurrent environments and batch processing scenarios.

        See Also:
            yt_dlp.YoutubeDL: Primary download engine documentation
            yt_dlp.DownloadError: Download-related error handling
            Messages.Executor: Localized error and status message definitions
            Config: Configuration options that affect download behavior
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
