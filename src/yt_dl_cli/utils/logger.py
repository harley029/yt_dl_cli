"""
Logging configuration factory module for the video downloader application.

This module provides a centralized logging configuration system that ensures
consistent logging behavior across the entire application. It sets up both
console and file-based logging with proper formatting and encoding support.

The module follows the factory pattern to create properly configured logger
instances while preventing common logging pitfalls such as duplicate handlers
and configuration conflicts.

Key Features:
- Dual output logging (console + file)
- Automatic log directory creation
- UTF-8 encoding support for international characters
- Singleton-like behavior to prevent handler duplication
- Consistent timestamp and level formatting
- Thread-safe logging operations

The logging system is designed to be robust and handle various edge cases
including missing directories, encoding issues, and multiple initialization
attempts.

Example:
    Basic usage of the logger factory:

    >>> from pathlib import Path
    >>> logger = LoggerFactory.get_logger(Path("logs"))
    >>> logger.info("Download started")
    >>> logger.error("Failed to process video")
    >>> logger.warning("Quality not available, using fallback")

Dependencies:
    - logging: Python standard library logging framework
    - pathlib: Cross-platform path handling
"""

import logging
from pathlib import Path


class LoggerFactory:
    """
    Factory class for creating and configuring logger instances.

    This factory handles the setup of logging configuration including both
    console and file output, ensuring consistent logging behavior throughout
    the application. It implements a singleton-like pattern for the root
    logger configuration to prevent duplicate handlers and configuration
    conflicts.

    The factory creates loggers with standardized formatting that includes
    timestamps, log levels, and message content. All log files are created
    with UTF-8 encoding to properly handle international characters in
    video titles and URLs.

    Design Pattern:
        This class follows the Factory Method pattern, providing a centralized
        way to create configured logger instances while encapsulating the
        complexity of logging setup.

    Thread Safety:
        The logging configuration is thread-safe as it relies on Python's
        built-in logging module, which handles concurrent access internally.

    Attributes:
        None (all methods are static)

    Example:
        >>> # Create logger for downloads directory
        >>> logger = LoggerFactory.get_logger(Path("downloads"))
        >>> logger.info("Application started")
        >>>
        >>> # Logger can be reused across modules
        >>> same_logger = LoggerFactory.get_logger(Path("downloads"))
        >>> same_logger.warning("This uses the same configuration")
    """

    def __init__(self):
        """
        Initialize the LoggerFactory instance.

        Creates a new instance of the logger factory. While all methods are
        static and don't require instance state, this constructor allows for
        consistent instantiation patterns and potential future extensibility.

        Note:
            All factory methods are static, so instantiation is optional.
            You can call LoggerFactory.get_logger() directly without
            creating an instance.

        Example:
            >>> # Both approaches work identically
            >>> factory = LoggerFactory()
            >>> logger1 = factory.get_logger(Path("logs"))
            >>>
            >>> # Direct static call (preferred)
            >>> logger2 = LoggerFactory.get_logger(Path("logs"))
        """

    @staticmethod
    def get_logger(save_dir: Path) -> logging.Logger:
        """
        Create and configure a logger instance with both console and file handlers.

        This method sets up a comprehensive logging system that outputs to both
        the console (for immediate feedback) and a log file (for persistent
        record keeping). The method ensures the target directory exists and
        configures the root logger only once to prevent duplicate log entries.

        The logging configuration includes:
        - INFO level logging (captures info, warning, error, and critical)
        - Timestamped log entries with ISO format
        - Standardized message format with level indicators
        - UTF-8 encoded file output for international character support
        - Both console and file output streams

        Args:
            save_dir (Path): Directory path where the log file will be created.
                           The directory will be created automatically if it
                           doesn't exist, including any parent directories.
                           Must be a valid pathlib.Path object.

        Returns:
            logging.Logger: Configured logger instance named "video_dl_cli"
                          ready for immediate use. The logger inherits from
                          the configured root logger and will output to both
                          console and the specified log file.

        Raises:
            OSError: May be raised if the save directory cannot be created
                    due to permission issues or invalid path specifications.
            PermissionError: Raised if the log file cannot be created or
                           written to due to insufficient permissions.

        Side Effects:
            - Creates the specified directory and any missing parent directories
            - Creates or appends to "download.log" file in the save directory
            - Configures the root logger (only on first call)
            - May create multiple file handles if called with different directories

        Example:
            >>> from pathlib import Path
            >>>
            >>> # Basic usage
            >>> logger = LoggerFactory.get_logger(Path("./logs"))
            >>> logger.info("Starting download process")
            >>> logger.error("Failed to connect to server")
            >>>
            >>> # With nested directory creation
            >>> logger = LoggerFactory.get_logger(Path("./app/logs/downloads"))
            >>> logger.warning("Using fallback quality setting")
            >>>
            >>> # Multiple loggers (same configuration)
            >>> logger1 = LoggerFactory.get_logger(Path("./logs"))
            >>> logger2 = LoggerFactory.get_logger(Path("./logs"))
            >>> # Both loggers share the same root configuration

        Log File Format:
            The log file entries follow this format:

                2024-01-15 14:30:25,123 [INFO] Download started for video XYZ
                2024-01-15 14:30:26,456 [ERROR] Network timeout occurred
                2024-01-15 14:30:27,789 [WARNING] Retrying download attempt

        Note:
            - Only configures the root logger once to avoid duplicate handlers
            - Subsequent calls with different directories will create additional
              file handlers but won't duplicate console output
            - The log file is created with UTF-8 encoding to handle international
              characters in video titles and URLs
            - Log level is set to INFO, so DEBUG messages won't appear
            - The save directory is created with parents=True and exist_ok=True
              for robust directory handling
        """
        # Ensure the save directory exists, creating parent directories as needed
        try:
            save_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            # Re-raise with more context for better error handling
            raise OSError(f"Failed to create log directory {save_dir}: {e}") from e

        # Get the root logger instance
        root = logging.getLogger()

        # Configure the root logger only once to prevent duplicate handlers
        if not root.handlers:
            try:
                logging.basicConfig(
                    level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[
                        # Console handler for immediate feedback
                        logging.StreamHandler(),
                        # File handler for persistent logging
                        logging.FileHandler(
                            save_dir / "download.log", encoding="utf-8"
                        ),
                    ],
                )
            except PermissionError as e:
                # Handle file creation permission errors
                raise PermissionError(
                    f"Cannot create log file in {save_dir}: {e}"
                ) from e

        # Return a named logger instance that inherits root configuration
        return logging.getLogger("video_dl_cli")
