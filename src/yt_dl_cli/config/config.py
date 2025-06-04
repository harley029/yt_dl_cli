from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from yt_dl_cli.i18n.messages import Messages


@dataclass
class Config:
    """
    Configuration data class containing all application settings.

    This class holds all the configuration parameters needed for the Video
    downloader application, including download paths, quality settings, and
    concurrency controls.

    Attributes:
        save_dir (Path): Directory where downloaded files will be saved
        max_workers (int): Maximum number of concurrent download threads
        quality (str): Video quality preference ('best', 'worst', '720', '480', '360')
        audio_only (bool): Whether to download only audio (MP3) instead of video
        urls (List[str]): List of URLs to download, defaults to empty list
    """

    save_dir: Path
    max_workers: int
    quality: str
    audio_only: bool
    urls: List[str] = field(default_factory=list)

    def __post_init__(self):
        """
        Validate configuration parameters after initialization.

        Ensures that all configuration values are within acceptable ranges
        and raises ValueError with descriptive messages if validation fails.
        """
        if self.max_workers < 1:
            raise ValueError(
                Messages.Config.INVALID_WORKERS(workers=self.max_workers)
            )

        valid_qualities = ["best", "worst", "720", "480", "360"]
        if self.quality not in valid_qualities:
            raise ValueError(
                Messages.Config.INVALID_QUALITY(
                    valid=f"{', '.join(valid_qualities)}", quality=self.quality
                )
            )
        if not isinstance(self.save_dir, Path):
            self.save_dir = Path(self.save_dir)
