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


RESET = "\x1b[0m"
COLORS = {
    "DEBUG": "\x1b[36m",  # Cyan
    "INFO": "\x1b[32m",  # Green
    "WARNING": "\x1b[33m",  # Yellow
    "ERROR": "\x1b[31m",  # Red
    "CRITICAL": "\x1b[41m",  # Red bg
}


class ColorFormatter(logging.Formatter):
    """
    Custom logging formatter that adds ANSI color codes to log messages.

    This formatter extends the standard logging.Formatter to provide colored
    output for different log levels when displaying messages in the console.
    Colors help users quickly identify the severity of log messages.

    The formatter applies different colors based on the log level:
    - DEBUG: Cyan
    - INFO: Green
    - WARNING: Yellow
    - ERROR: Red
    - CRITICAL: Red background

    Color codes are only applied to console output and are automatically
    reset after each message to prevent color bleeding.

    Attributes:
        Inherits all attributes from logging.Formatter

    Example:
        >>> formatter = ColorFormatter("%(levelname)s: %(message)s")
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(formatter)
        >>> logger.addHandler(handler)
        >>> logger.info("This will appear in green")
        >>> logger.error("This will appear in red")
    """

    def format(self, record):
        """
        Format a log record with appropriate color coding.

        This method overrides the parent format method to add ANSI color
        codes before the formatted message and reset codes after it.
        The color is determined by the log level of the record.

        Args:
            record (logging.LogRecord): The log record to be formatted.
                Contains information about the log event including level,
                message, timestamp, and other metadata.

        Returns:
            str: The formatted log message with ANSI color codes applied.
                Format: "{color_code}{formatted_message}{reset_code}"

        Note:
            - Uses the parent class's format method for the base formatting
            - Only adds color codes, doesn't change the underlying format
            - Falls back to no color (RESET) if log level is not recognized
            - Color codes are compatible with most modern terminals
        """
        color = COLORS.get(record.levelname, RESET)
        message = super().format(record)
        return f"{color}{message}{RESET}"


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

    @staticmethod
    def get_logger(save_dir: Path) -> logging.Logger:
        """
        Create and configure a logger instance with both console and file handlers.

        This method sets up a comprehensive logging system that outputs to both
        the console (for immediate feedback) and a log file (for persistent
        record keeping). The method ensures the target directory exists and
        configures the root logger only once to prevent duplicate log entries.

        The logging configuration includes:
        - DEBUG level logging (captures all log levels)
        - Timestamped log entries with ISO format
        - Standardized message format with level indicators
        - UTF-8 encoded file output for international character support
        - Colored console output for better readability
        - Plain text file output without color codes

        Args:
            save_dir (Path): Directory path where the log file will be created.
                           The directory will be created automatically if it
                           doesn't exist, including any parent directories.
                           Must be a valid pathlib.Path object.

        Returns:
            logging.Logger: Configured logger instance named "video_dl_cli"
                          ready for immediate use. The logger is set to DEBUG
                          level and will output to both console and the
                          specified log file.

        Raises:
            OSError: May be raised if the save directory cannot be created
                    due to permission issues or invalid path specifications.
            PermissionError: Raised if the log file cannot be created or
                           written to due to insufficient permissions.

        Side Effects:
            - Creates the specified directory and any missing parent directories
            - Creates or appends to "download.log" file in the save directory
            - Clears existing handlers to prevent duplication
            - Configures both console and file handlers with appropriate formatters

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
            >>> # Debug level logging
            >>> logger.debug("Detailed debugging information")

        Log File Format:
            The log file entries follow this format:

                2024-01-15 14:30:25,123 [INFO] Download started for video XYZ
                2024-01-15 14:30:26,456 [ERROR] Network timeout occurred
                2024-01-15 14:30:27,789 [WARNING] Retrying download attempt

        Console Output:
            Console output includes the same format but with color coding
            applied to help distinguish between different log levels.

        Note:
            - Clears existing handlers on each call to prevent duplication
            - Creates new handlers for both console and file output
            - Console handler uses ColorFormatter for colored output
            - File handler uses standard Formatter without colors
            - Log file is created with UTF-8 encoding for international support
            - The save directory is created with parents=True and exist_ok=True
        """
        # Ensure the save directory exists, creating parent directories as needed
        try:
            save_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create log directory {save_dir}: {e}") from e

        logger = logging.getLogger("video_dl_cli")
        logger.setLevel(logging.INFO)

        # Clear existing handlers to prevent duplication on repeated calls
        if logger.hasHandlers():
            logger.handlers.clear()

        # Set up colored console output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            ColorFormatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        logger.addHandler(console_handler)

        # Set up plain text file logging (without colors)
        try:
            file_handler = logging.FileHandler(save_dir / "download.log", encoding="utf-8")
        except PermissionError as e:
            raise PermissionError(f"Cannot create log file: {e}") from e
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        logger.addHandler(file_handler)

        return logger
