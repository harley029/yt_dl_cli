from abc import ABC, abstractmethod
from typing import Dict, Any


class IFormatStrategy(ABC):
    @abstractmethod
    def get_opts(self) -> Dict[str, Any]:
        pass


class VideoFormatStrategy(IFormatStrategy):
    def __init__(self, quality: str):
        self.quality = quality

    def get_opts(self) -> Dict[str, Any]:
        if self.quality == "best":
            fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
        elif self.quality == "worst":
            fmt = "worst[ext=mp4]"
        else:
            fmt = f"best[height<={self.quality}][ext=mp4]"
        return {"format": fmt, "merge_output_format": "mp4"}


class AudioFormatStrategy(IFormatStrategy):
    def get_opts(self) -> Dict[str, Any]:
        return {"format": "bestaudio/best", "extractaudio": True, "audioformat": "mp3"}


def get_strategy(config) -> IFormatStrategy:
    return (
        AudioFormatStrategy()
        if config.audio_only
        else VideoFormatStrategy(config.quality)
    )
