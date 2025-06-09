import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from yt_dl_cli.utils.stats_manager import StatsManager


def test_stats_manager_counts():
    """ Testing of StatsManager.counts  """
    stats = StatsManager()
    stats.record_success()
    stats.record_skip()
    stats.record_failure()
    assert stats.success == 1
    assert stats.skipped == 1
    assert stats.failed == 1
