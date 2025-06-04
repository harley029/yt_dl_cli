"""
YouTube Downloader Main Application Module.

This module contains the primary VideoDownloader class that serves as the main
orchestrator for the entire video downloading process. It integrates all
components of the application including configuration management, dependency
injection, asynchronous orchestration, and comprehensive error handling.

The module is designed with a clean architecture approach, separating concerns
between configuration, logging, orchestration, and execution. It provides a
high-level interface that abstracts away the complexity of concurrent downloads,
internationalization, and error management.

Key Features:
    - Command-line argument parsing and configuration management
    - Dependency injection for clean component integration
    - Asynchronous download orchestration for optimal performance
    - Comprehensive error handling with user-friendly messages
    - Internationalization support for multi-language environments
    - Graceful handling of user interruptions and system errors

Architecture:
    The module follows the dependency injection pattern to ensure loose coupling
    between components. The VideoDownloader class acts as a facade that coordinates
    between different subsystems without being tightly coupled to their implementations.

Example:
    Basic usage as a standalone script:

    $ python main.py --url "https://youtube.com/watch?v=example" --quality 720p

    Or programmatic usage:

    >>> from main import VideoDownloader
    >>> downloader = VideoDownloader()
    >>> downloader.download()

Author: Oleksandr Kharhenko
License: MIT
"""

import asyncio
import logging
from typing import Optional

from yt_dl_cli.config.config import Config
from yt_dl_cli.utils.logger import LoggerFactory
from yt_dl_cli.core.orchestration import AsyncOrchestrator, DIContainer
from yt_dl_cli.utils.parser import parse_arguments

# -------------------- Internationalization --------------------
from yt_dl_cli.i18n.init import setup_i18n
setup_i18n()  # noqa: E402
from yt_dl_cli.i18n.messages import Messages


class VideoDownloader:
    """
    Main orchestrator class for the YouTube video downloading application.

    This class serves as the primary entry point and coordinator for the entire
    download process. It encapsulates the complexity of managing configuration,
    dependency injection, asynchronous orchestration, and error handling while
    providing a simple interface for initiating downloads.

    The class follows the facade pattern, providing a simplified interface to
    a complex subsystem of downloaders, parsers, loggers, and orchestrators.
    It ensures proper initialization order, resource management, and graceful
    error handling throughout the application lifecycle.

    Responsibilities:
        1. Parse and validate command-line arguments
        2. Initialize configuration and logging systems
        3. Create and configure the dependency injection container
        4. Orchestrate asynchronous download operations
        5. Handle user interruptions and system errors gracefully
        6. Manage resource cleanup and proper shutdown procedures

    Design Patterns:
        - Facade: Simplifies interaction with complex subsystems
        - Dependency Injection: Promotes loose coupling and testability
        - Context Manager: Ensures proper resource management

    Thread Safety:
        This class is not thread-safe by design. Each instance should be used
        in a single thread context. For concurrent operations, the class
        delegates to AsyncOrchestrator which handles async/await patterns.

    Attributes:
        config (Config): Application configuration object containing all
                        settings for download operations, paths, and preferences.
        logger (logging.Logger): Configured logger instance for the application,
                               set up with appropriate handlers and formatters.

    Example:
        Basic usage with default configuration:

        >>> downloader = VideoDownloader()
        >>> downloader.download()

        Usage with custom configuration:

        >>> custom_config = Config(save_dir="/custom/path", quality="1080p")
        >>> custom_logger = logging.getLogger("custom")
        >>> downloader = VideoDownloader(config=custom_config, logger=custom_logger)
        >>> downloader.download()

    See Also:
        Config: Configuration management class
        AsyncOrchestrator: Handles concurrent download operations
        DIContainer: Dependency injection container for component creation
        LoggerFactory: Factory for creating configured logger instances
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        logger: Optional[logging.Logger] = None,
        language: Optional[str] = None,
    ):
        """
        Initialize the VideoDownloader with configuration and logging setup.

        This constructor sets up the fundamental components required for the
        download process. It allows for dependency injection of configuration
        and logger objects, falling back to defaults when not provided.

        The initialization process:
        1. Resolves configuration from provided config or command-line arguments
        2. Sets up internationalization with the specified or detected language
        3. Sets up logging infrastructure with appropriate handlers
        4. Prepares the instance for download operations

        Args:
            config (Optional[Config], optional): Pre-configured Config object
                containing application settings. If None, configuration will
                be parsed from command-line arguments using parse_arguments().
                Defaults to None.
            logger (Optional[logging.Logger], optional): Pre-configured logger
                instance for application logging. If None, a new logger will
                be created using LoggerFactory with the save directory from
                config. Defaults to None.
            language (Optional[str], optional): Language code for internationalization
                (e.g., 'ru', 'en', 'de'). If None, uses system default locale.
                Defaults to None.

        Raises:
            ConfigurationError: If the provided config is invalid or if
                               command-line argument parsing fails.
            LoggerInitializationError: If logger setup fails due to permissions
                                     or invalid configuration.
            ImportError: If required dependencies for internationalization
                        or core components are not available.

        Note:
            The constructor does not perform any I/O operations or network
            requests. All heavy operations are deferred to the download()
            method to keep initialization lightweight and predictable.

        Example:
            Default initialization:

            >>> downloader = VideoDownloader()

            Custom configuration:

            >>> config = Config(save_dir="/downloads", quality="720p")
            >>> downloader = VideoDownloader(config=config)

            Full customization with language:

            >>> config = Config(save_dir="/downloads")
            >>> logger = logging.getLogger("my_app")
            >>> downloader = VideoDownloader(config=config, logger=logger, language="ru")
        """
        # Настраиваем интернационализацию ПЕРЕД парсингом конфигурации
        setup_i18n(language=language)

        # Парсим конфигурацию и настраиваем логгер
        self.config = config or parse_arguments()
        self.logger = logger or LoggerFactory.get_logger(self.config.save_dir)

    def download(self) -> None:
        """
        Execute the complete video download process with comprehensive error handling.

        This method orchestrates the entire download workflow from initialization
        to completion. It creates the necessary components through dependency
        injection, sets up asynchronous orchestration, and manages the complete
        lifecycle of the download process.

        The method implements a robust error handling strategy that distinguishes
        between different types of failures and provides appropriate user feedback.
        It uses a context manager pattern to ensure proper resource cleanup
        regardless of how the process terminates.

        Process Flow:
            1. Create downloader core through dependency injection container
            2. Initialize AsyncOrchestrator with core and configuration
            3. Enter context manager for resource management
            4. Launch asynchronous download orchestration
            5. Handle completion or interruption gracefully
            6. Ensure proper cleanup of resources

        Returns:
            None: This method doesn't return a value. Success is indicated by
                 completion without exceptions, while failures are communicated
                 through logging and appropriate exit codes.

        Raises:
            KeyboardInterrupt: Caught and handled gracefully when user presses
                             Ctrl+C. Logs a warning message and performs cleanup.
            SystemExit: May be raised by underlying components for critical
                       errors that require immediate termination.
            Exception: Any other unexpected errors are caught, logged as critical
                      errors with full exception details, and handled gracefully.

        Side Effects:
            - Creates files in the configured save directory
            - Writes log entries to configured log destinations
            - May create temporary files during download process
            - Updates progress indicators and statistics
            - May modify system network settings (proxy, timeout)

        Error Handling Strategy:
            - User Interruption (KeyboardInterrupt): Graceful shutdown with
              warning message, allowing for cleanup and partial progress saving
            - Critical Errors (Exception): Full error logging with exception
              details, graceful termination to prevent data corruption
            - Resource Management: Context manager ensures cleanup even if
              exceptions occur during the download process

        Performance Considerations:
            - Utilizes asyncio for concurrent downloads to maximize throughput
            - Implements proper resource management to prevent memory leaks
            - Delegates heavy operations to specialized orchestrator components
            - Provides progress tracking and statistics for user feedback

        Example:
            Basic download execution:

            >>> downloader = VideoDownloader()
            >>> downloader.download()
            # Starts download process, handles user input, shows progress

            Error handling demonstration:

            >>> try:
            ...     downloader.download()
            ... except SystemExit:
            ...     print("Download process terminated")

        Note:
            This method is designed to be called once per VideoDownloader
            instance. Multiple calls may result in undefined behavior due
            to resource state management. Create a new instance for each
            independent download session.

        See Also:
            DIContainer.create_downloader_core: Creates the core download engine
            AsyncOrchestrator: Manages concurrent download operations
            Messages.CLI: Internationalized user messages for error reporting
        """
        core = DIContainer.create_downloader_core(self.config, logger=self.logger)
        orchestrator = AsyncOrchestrator(core, self.config)
        try:
            with core:
                asyncio.run(orchestrator.run())
        except KeyboardInterrupt:
            core.logger.warning(Messages.CLI.USER_INTERRUPT())
        except Exception as e:
            core.logger.critical(Messages.CLI.CRITICAL_ERROR(error=e))


if __name__ == "__main__":
    downloader = VideoDownloader()
    downloader.download()

