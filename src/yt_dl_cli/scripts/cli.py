"""
Command Line Interface Entry Point Module for YT-DL-CLI Tool.

This module serves as the primary entry point for the video downloader command-line
interface application. It provides a simple interface to initialize and execute
the video downloading functionality through the main VideoDownloader class.

The module implements a clean separation of concerns by delegating the actual
downloading logic to the main application module while providing a lightweight
CLI wrapper for user interaction.

Example:
    This module is typically executed as a script or called from a package
    entry point:

    $ python scripts/cli.py

    Or when installed as a package:

    $ yt-dl-cli
"""

from yt_dl_cli.main import VideoDownloader  # type: ignore[import-untyped]


def main():
    """
    Main entry point function for the YT-DL-CLI application.

    This function serves as the primary interface between the command-line
    environment and the core downloading functionality. It instantiates the
    VideoDownloader class and initiates the download process.

    The function follows the single responsibility principle by focusing solely
    on application initialization and delegation to the core downloader logic.
    It handles the high-level orchestration while leaving specific download
    operations to the VideoDownloader class.

    Workflow:
        1. Creates a new VideoDownloader instance
        2. Calls the download method to start the download process
        3. The VideoDownloader handles all user interaction, configuration,
           and actual downloading operations

    Returns:
        NoReturn: This function typically runs indefinitely or exits the
                 program upon completion, so it doesn't return a value.

    Raises:
        SystemExit: May be raised by the VideoDownloader if a critical error
                   occurs or when the user requests to exit the application.
        KeyboardInterrupt: May be raised if the user interrupts the process
                          with Ctrl+C, though this should be handled by the
                          VideoDownloader class.
        ImportError: May be raised if the main module or VideoDownloader
                    class cannot be imported due to missing dependencies
                    or incorrect module structure.

    Note:
        This function expects the VideoDownloader class to handle all user
        interaction, error handling, and graceful shutdown procedures.
        Any configuration or initialization parameters should be handled
        within the VideoDownloader class itself.

    See Also:
        main.VideoDownloader: The core class that handles all download operations
        config.config: Configuration management for the application
        core.orchestration: Main orchestration logic for download workflows
    """
    downloader = VideoDownloader()
    downloader.download()
