"""
Format strategy implementations for media download configuration.

This module implements the Strategy design pattern to provide flexible format
selection for media downloads. It abstracts the complexity of format specification
into discrete strategy classes, allowing for easy extension and testing of
different download configurations.

The module provides strategies for both video and audio-only downloads, with
configurable quality settings and format preferences optimized for compatibility
and user experience. The factory function enables clean separation between
configuration parsing and strategy instantiation.

Classes:
    IFormatStrategy: Abstract base class defining the strategy interface
    VideoFormatStrategy: Concrete strategy for video downloads with quality control
    AudioFormatStrategy: Concrete strategy for audio-only downloads

Functions:
    get_strategy: Factory function for creating appropriate strategy instances

Design Patterns:
    - Strategy Pattern: Encapsulates format selection algorithms
    - Factory Pattern: Provides centralized strategy instantiation
    - Abstract Base Class: Ensures consistent interface across strategies

Example:
    Basic usage with different configurations:

    >>> from format_strategies import get_strategy
    >>>
    >>> # Audio download configuration
    >>> class AudioConfig:
    ...     audio_only = True
    ...     quality = "best"
    >>>
    >>> audio_strategy = get_strategy(AudioConfig())
    >>> audio_opts = audio_strategy.get_opts()
    >>> print(audio_opts)
    {'format': 'bestaudio/best', 'extractaudio': True, 'audioformat': 'mp3'}

    >>> # High-quality video configuration
    >>> class VideoConfig:
    ...     audio_only = False
    ...     quality = "1080"
    >>>
    >>> video_strategy = get_strategy(VideoConfig())
    >>> video_opts = video_strategy.get_opts()
    >>> print(video_opts)
    {'format': 'best[height<=1080][ext=mp4]', 'merge_output_format': 'mp4'}

Note:
    The strategies are designed to work with yt-dlp library format specifications,
    but the pattern can be adapted for other download libraries by modifying
    the option dictionaries returned by get_opts() methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IFormatStrategy(ABC):
    """Abstract base class defining the interface for download format strategies.

    This interface follows the Strategy pattern to encapsulate different
    format selection algorithms for media downloads. Each concrete strategy
    implements specific logic for choosing appropriate download formats
    and options.
    """

    @abstractmethod
    def get_opts(self) -> Dict[str, Any]:
        """Get download options dictionary for the specific format strategy.

        Returns:
            Dict[str, Any]: A dictionary containing format-specific options
            that can be passed to a download library (e.g., yt-dlp).

        Raises:
            NotImplementedError: If called on the abstract base class.
        """


class VideoFormatStrategy(IFormatStrategy):
    """Strategy for downloading video content with configurable quality settings.

    This strategy handles video downloads with quality preferences ranging
    from best available quality to specific resolution limits. It prioritizes
    MP4 format for better compatibility across devices and platforms.

    Attributes:
        quality (str): Quality setting that determines format selection.
            Supported values:
            - "best": Downloads highest quality video+audio
            - "worst": Downloads lowest quality video
            - Numeric string (e.g., "720"): Downloads best video up to specified height
    """

    def __init__(self, quality: str):
        """Initialize the video format strategy with a quality setting.

        Args:
            quality (str): The desired video quality. Accepts "best", "worst",
                or a numeric string representing maximum height in pixels.

        Example:
            >>> strategy = VideoFormatStrategy("720")
            >>> strategy = VideoFormatStrategy("best")
        """
        self.quality = quality

    def get_opts(self) -> Dict[str, Any]:
        """Generate video download options based on the quality setting.

        Creates format selector strings optimized for video downloads:
        - For "best": Selects best video+audio combination in MP4
        - For "worst": Selects lowest quality MP4 video
        - For numeric values: Selects best video up to specified height

        Returns:
            Dict[str, Any]: Download options dictionary containing:
                - "format": Format selector string for video selection
                - "merge_output_format": Output container format (MP4)

        Example:
            >>> strategy = VideoFormatStrategy("720")
            >>> opts = strategy.get_opts()
            >>> print(opts)
            {'format': 'best[height<=720][ext=mp4]', 'merge_output_format': 'mp4'}
        """
        if self.quality == "best":
            fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
        elif self.quality == "worst":
            fmt = "worst[ext=mp4]"
        else:
            fmt = f"best[height<={self.quality}][ext=mp4]"
        return {"format": fmt, "merge_output_format": "mp4"}


class AudioFormatStrategy(IFormatStrategy):
    """Strategy for downloading audio-only content in MP3 format.

    This strategy extracts and converts audio streams to MP3 format,
    providing a consistent audio-only download experience regardless
    of the source video format.
    """

    def get_opts(self) -> Dict[str, Any]:
        """Generate audio-only download options.

        Configures the download to extract the best available audio stream
        and convert it to MP3 format for universal compatibility.

        Returns:
            Dict[str, Any]: Download options dictionary containing:
                - "format": Audio format selector for best quality audio
                - "extractaudio": Boolean flag to enable audio extraction
                - "audioformat": Target audio format (MP3)

        Example:
            >>> strategy = AudioFormatStrategy()
            >>> opts = strategy.get_opts()
            >>> print(opts)
            {'format': 'bestaudio/best', 'extractaudio': True, 'audioformat': 'mp3'}
        """
        return {"format": "bestaudio/best", "extractaudio": True, "audioformat": "mp3"}


def get_strategy(config) -> IFormatStrategy:
    """Factory function to create appropriate format strategy based on configuration.

    This function implements the Factory pattern to instantiate the correct
    strategy based on the provided configuration object. It abstracts the
    strategy selection logic from the client code.

    Args:
        config: Configuration object that must have at least the following attributes:
            - audio_only (bool): Flag indicating if only audio should be downloaded
            - quality (str): Video quality setting (used only when audio_only is False)

    Returns:
        IFormatStrategy: An instance of either AudioFormatStrategy or
        VideoFormatStrategy based on the configuration.

    Example:
        >>> class Config:
        ...     def __init__(self, audio_only=False, quality="best"):
        ...         self.audio_only = audio_only
        ...         self.quality = quality
        >>>
        >>> audio_config = Config(audio_only=True)
        >>> strategy = get_strategy(audio_config)
        >>> isinstance(strategy, AudioFormatStrategy)
        True
        >>>
        >>> video_config = Config(audio_only=False, quality="720")
        >>> strategy = get_strategy(video_config)
        >>> isinstance(strategy, VideoFormatStrategy)
        True
    """
    return (
        AudioFormatStrategy()
        if config.audio_only
        else VideoFormatStrategy(config.quality)
    )
