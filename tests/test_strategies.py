import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from yt_dl_cli.interfaces.strategies import VideoFormatStrategy, AudioFormatStrategy


def test_video_strategy_best():
    strategy = VideoFormatStrategy("best")
    opts = strategy.get_opts()
    assert opts["format"] == "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
    assert opts["merge_output_format"] == "mp4"


def test_video_strategy_worst():
    strategy = VideoFormatStrategy("worst")
    opts = strategy.get_opts()
    assert opts["format"] == "worst[ext=mp4]"
    assert opts["merge_output_format"] == "mp4"


def test_video_strategy_numeric_720():
    strategy = VideoFormatStrategy("720")
    opts = strategy.get_opts()
    assert opts["format"] == "best[height<=720][ext=mp4]"
    assert opts["merge_output_format"] == "mp4"


def test_video_strategy_numeric_other():
    strategy = VideoFormatStrategy("480")
    opts = strategy.get_opts()
    assert opts["format"] == "best[height<=480][ext=mp4]"
    assert opts["merge_output_format"] == "mp4"


def test_audio_strategy():
    strategy = AudioFormatStrategy()
    opts = strategy.get_opts()
    assert opts["format"] == "bestaudio/best"
    assert opts["extractaudio"] is True
    assert opts["audioformat"] == "mp3"
