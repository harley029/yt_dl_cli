"""
Internationalization and message handling for user-facing text.

This module provides a comprehensive system for managing all user-facing messages
in the application with support for internationalization (i18n). It implements
lazy translation loading to ensure messages are translated at display time rather
than at module import time, which is crucial for proper localization support.

The module is organized into logical message groups corresponding to different
application components, making it easy to maintain and extend. Each message
uses the LazyTranslation pattern to defer translation until the message is
actually needed, ensuring the correct locale is used.

Key Features:
    - Lazy translation loading for proper i18n support
    - Organized message groups by application component
    - Colorized console output with cross-platform support
    - Template-based messages with parameter substitution
    - Clean separation between message definitions and display logic

Example:
    Basic usage of messages and console output:

    >>> from messages import Messages, console_printer
    >>>
    >>> # Display a configuration error
    >>> error_msg = Messages.Config.INVALID_WORKERS(workers=0)
    >>> console_printer.printout("red", error_msg)
    >>>
    >>> # Display download progress
    >>> start_msg = Messages.Core.START_DOWNLOAD(title="Example Video")
    >>> console_printer.printout("blue", start_msg)
"""


class LazyTranslation:
    """
    Deferred translation wrapper for internationalization support.

    This class implements lazy evaluation of translatable strings, ensuring
    that translation occurs at display time rather than at module load time.
    This is essential for proper internationalization because:

    1. The user's locale may not be determined at import time
    2. The translation system may not be initialized when modules are loaded
    3. The same message may need to be displayed in different locales during runtime

    The class stores the message template and defers both translation and
    string formatting until the message is actually needed for display.

    Attributes:
        template (str): The original message template with optional format placeholders.

    Example:
        >>> msg = LazyTranslation("Hello {name}!")
        >>> # Translation and formatting happen when called:
        >>> translated_msg = msg(name="World")
        >>> print(translated_msg)  # "Hello World!" (or translated equivalent)
    """

    def __init__(self, template: str):
        """
        Initialize a lazy translation wrapper.

        Args:
            template (str): The message template string. May contain format
                placeholders (e.g., {name}, {count}) for runtime substitution.
                The template will be passed to the translation function when
                the message is displayed.

        Example:
            >>> greeting = LazyTranslation("Welcome, {username}!")
            >>> error_msg = LazyTranslation("File not found: {filename}")
        """
        self.template = template

    def __call__(self, **kwargs) -> str:
        """
        Translate and format the message with provided parameters.

        This method performs the actual translation by looking up the global
        translation function _() and applying it to the template. If keyword
        arguments are provided, they are used for string formatting after
        translation.

        The translation function is looked up dynamically from the builtins
        namespace, allowing it to be set up by the i18n initialization code
        without creating import dependencies.

        Args:
            **kwargs: Keyword arguments for string formatting. These are passed
                to str.format() after translation is applied.

        Returns:
            str: The translated and formatted message string ready for display.

        Example:
            >>> msg = LazyTranslation("Downloaded {count} files")
            >>> result = msg(count=42)
            >>> print(result)  # "Downloaded 42 files" (or translated)
        """
        import builtins

        _ = builtins.__dict__.get("_", lambda x: x)
        return _(self.template).format(**kwargs) if kwargs else _(self.template)

    def __str__(self) -> str:
        """
        Prevent direct string conversion to catch programming errors.

        This method deliberately raises an error to prevent LazyTranslation
        objects from being used directly as strings. This helps catch bugs
        where messages are not properly called as functions, which would
        bypass both translation and parameter substitution.

        Returns:
            Never returns - always raises RuntimeError.

        Raises:
            RuntimeError: Always raised to indicate improper usage.
                The error message provides guidance on correct usage.

        Example:
            >>> msg = LazyTranslation("Hello!")
            >>> str(msg)  # Raises RuntimeError
            >>> msg()     # Correct usage - returns translated string
        """
        raise RuntimeError(
            "Do not use LazyTranslation objects directly! "
            "Call as a function, e.g. Messages.Stats.TITLE()"
        )


class Messages:
    """
    Container for all user-facing messages in the application.

    This class serves as a centralized registry for all translatable strings
    used throughout the application. Messages are organized into nested classes
    that correspond to different application components, making it easy to
    locate and maintain related messages.

    Each message is wrapped in a LazyTranslation object to support proper
    internationalization. The hierarchical organization allows for:

    - Easy maintenance and updates of message text
    - Clear association between messages and application components
    - Efficient organization for translation tools and translators
    - Type-safe access to messages through the class hierarchy

    The message groups are designed to match the application's architecture,
    with separate groups for configuration, core functionality, CLI interface,
    statistics, and various processing components.

    Example:
        >>> # Access configuration-related messages
        >>> error = Messages.Config.INVALID_WORKERS(workers=0)
        >>>
        >>> # Access download progress messages
        >>> start = Messages.Core.START_DOWNLOAD(title="My Video")
        >>> done = Messages.Core.DONE_DOWNLOAD(title="My Video")
    """

    class Config:
        """
        Messages for configuration validation and errors.

        This group contains all messages related to application configuration,
        including validation errors, invalid parameter notifications, and
        configuration-related warnings. These messages are typically displayed
        during application startup or when processing command-line arguments.
        """

        INVALID_WORKERS = LazyTranslation(
            "max_workers must be at least 1, got {workers}"
        )
        """Message displayed when an invalid worker count is specified."""

        INVALID_QUALITY = LazyTranslation(
            "quality must be one of: {valid}, got {quality}"
        )
        """Message displayed when an unsupported quality setting is specified."""

    class Core:
        """
        Messages used by the core downloader component.

        This group contains messages related to the primary download functionality,
        including progress updates, completion notifications, and core operational
        messages. These are the most frequently displayed messages during normal
        application operation.
        """

        SKIP_EXISTS = LazyTranslation("[SKIP] Already exists: {title}")
        """Message displayed when a download is skipped because the file already exists."""

        START_DOWNLOAD = LazyTranslation("[START] {title}")
        """Message displayed when beginning a download operation."""

        DONE_DOWNLOAD = LazyTranslation("[DONE] {title}")
        """Message displayed when a download completes successfully."""

        ERROR_RESOURCE_CLOSE = LazyTranslation("Error closing resource: {error}")
        """Message displayed when there's an error during resource cleanup."""

    class Extractor:
        """
        Messages used by the video extractor component.

        This group contains messages related to video information extraction,
        which occurs before the actual download process. These messages help
        users understand issues with URL processing and metadata extraction.
        """

        ERROR_EXTRACT = LazyTranslation("Failed to extract info for {url}: {error}")
        """Message displayed when video information extraction fails for a specific URL."""

        ERROR_NO_INFO = LazyTranslation("Unable to extract video info")
        """Generic message displayed when video information cannot be extracted."""

    class Executor:
        """
        Messages used by the download executor component.

        This group contains messages related to the actual download execution
        process, including error messages for failed downloads and executor-specific
        operational messages.
        """

        ERROR_DOWNLOAD = LazyTranslation("Download failed for {url}: {error}")
        """Message displayed when a download operation fails."""

    class Stats:
        """
        Messages and formatting used for statistics reporting.

        This group contains both translatable messages and formatting constants
        used to display download statistics and summary reports. The constants
        (HEADER, FOOTER) are not translatable as they are decorative elements.
        """

        HEADER = "=" * 40
        """Decorative header line for statistics reports."""

        TITLE = LazyTranslation("DOWNLOAD SUMMARY:")
        """Title heading for the statistics summary."""

        PROCESSED = LazyTranslation("Processed:    {total}")
        """Message showing total number of items processed."""

        SUCCESSFUL = LazyTranslation("  Successful: {success}")
        """Message showing number of successful downloads."""

        SKIPPED = LazyTranslation("  Skipped:    {skipped}")
        """Message showing number of skipped downloads."""

        FAILED = LazyTranslation("  Failed:     {failed}")
        """Message showing number of failed downloads."""

        ELAPSED = LazyTranslation("Elapsed time: {elapsed:.2f}s")
        """Message showing total elapsed time for the operation."""

        FOOTER = "=" * 40
        """Decorative footer line for statistics reports."""

    class Orchestrator:
        """
        Messages used by the async orchestrator.

        This group contains messages related to the high-level coordination
        of download operations, including startup messages and orchestration
        status updates.
        """

        NO_URLS = LazyTranslation("No URLs to download.")
        """Message displayed when no URLs are provided for download."""

        STARTING = LazyTranslation(
            "Starting download of {count} items with {workers} workers"
        )
        """Message displayed when beginning a batch download operation."""

    class CLI:
        """
        Messages used in the command-line interface.

        This group contains messages specific to the command-line interface,
        including file handling errors, user interaction messages, and
        CLI-specific error conditions.
        """

        FILE_NOT_FOUND = LazyTranslation("Error: file '{file}' not found")
        """Message displayed when a specified input file cannot be found."""

        FILE_READ_ERROR = LazyTranslation("Error reading '{file}': {error}")
        """Message displayed when there's an error reading an input file."""

        USER_INTERRUPT = LazyTranslation("Download interrupted by user.")
        """Message displayed when the user interrupts the download process (Ctrl+C)."""

        CRITICAL_ERROR = LazyTranslation("Critical error: {error}")
        """Message displayed for critical errors that cause application termination."""
