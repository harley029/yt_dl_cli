"""
Configuration Management Module

This module provides configuration management functionality for the video downloader application.
It defines the Config dataclass that holds all application settings including download paths,
quality preferences, concurrency controls, and validation logic.

The module ensures configuration integrity through automatic validation and type conversion,
providing a centralized way to manage application settings with proper error handling.

Classes:
    **Config**: Main configuration dataclass with validation
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from yt_dl_cli.i18n.messages import Messages


@dataclass
class Config:
    """
    Configuration data class containing all application settings.

    This class holds all the configuration parameters needed for the YouTube
    downloader application, including download paths, quality settings, and
    concurrency controls. It provides automatic validation of configuration
    values and type conversion where appropriate.

    Attributes:
        save_dir (Path): Directory where downloaded files will be saved.
                        Automatically converted to Path object if string is provided.
        max_workers (int): Maximum number of concurrent download threads.
                          Must be at least 1.
        quality (str): Video quality preference. Valid options are:
                      'best', 'worst', '720', '480', '360'.
        audio_only (bool): Whether to download only audio (MP3) instead of video.
        urls (List[str]): List of URLs to download. Defaults to empty list.

    Raises:
        ValueError: If max_workers is less than 1 or quality is not in valid options.

    Example:
        >>> from pathlib import Path
        >>> config = Config(
        ...     save_dir=Path("/downloads"),
        ...     max_workers=4,
        ...     quality="720",
        ...     audio_only=False,
        ...     urls=["https://example.com/video1", "https://example.com/video2"]
        ... )
    """

    save_dir: Path
    max_workers: int
    quality: str
    audio_only: bool
    urls: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Validate configuration parameters after initialization.

        Ensures that all configuration values are within acceptable ranges
        and converts string paths to Path objects. This method is automatically
        called by the dataclass after object initialization.

        Validation rules:
        - max_workers must be at least 1
        - quality must be one of: 'best', 'worst', '720', '480', '360'
        - save_dir is converted to Path object if provided as string

        Raises:
            ValueError: If max_workers is less than 1 with descriptive message.
            ValueError: If quality is not in the list of valid options with
                       details about valid choices.

        Example:
            >>> # This will raise ValueError
            >>> config = Config(
            ...     save_dir=Path("/downloads"),
            ...     max_workers=0,  # Invalid: less than 1
            ...     quality="720",
            ...     audio_only=False
            ... )
            ValueError: Invalid number of workers: 0. Must be at least 1.
        """
        if self.max_workers < 1:
            raise ValueError(Messages.Config.INVALID_WORKERS(workers=self.max_workers))

        valid_qualities = ["best", "worst", "720", "480", "360"]
        if self.quality not in valid_qualities:
            raise ValueError(
                Messages.Config.INVALID_QUALITY(
                    valid=f"{', '.join(valid_qualities)}", quality=self.quality
                )
            )
        if not isinstance(self.save_dir, Path):
            self.save_dir = Path(self.save_dir)
