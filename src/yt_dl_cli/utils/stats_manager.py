from dataclasses import dataclass
from typing import Dict

from yt_dl_cli.interfaces.interfaces import ILogger
from yt_dl_cli.i18n.messages import Messages


@dataclass
class StatsManager:
    """
    Statistics manager for tracking download operations and generating reports.

    This class maintains counters for different types of download outcomes
    and provides methods for recording events and generating summary reports.

    Attributes:
        success (int): Count of successful downloads
        failed (int): Count of failed downloads
        skipped (int): Count of skipped downloads (files already exist)
    """

    success: int = 0
    failed: int = 0
    skipped: int = 0

    def record_success(self) -> None:
        """Increment the success counter by one."""
        self.success += 1

    def record_failure(self) -> None:
        """Increment the failure counter by one."""
        self.failed += 1

    def record_skip(self) -> None:
        """Increment the skip counter by one."""
        self.skipped += 1

    def get_summary(self) -> Dict[str, int]:
        """
        Calculate and return a summary of all statistics.

        Returns:
            Dict[str, int]: Dictionary containing success, failed, skipped, and
            total counts
        """
        total = self.success + self.failed + self.skipped
        return {
            "success": self.success,
            "failed": self.failed,
            "skipped": self.skipped,
            "total": total,
        }

    def report(self, logger: ILogger, elapsed: float) -> None:
        """
        Generate and log a formatted summary report of download statistics.

        Creates a detailed report showing the breakdown of download results
        and total elapsed time, formatted with visual separators.

        Args:
            logger (ILogger): Logger instance to output the report
            elapsed (float): Total elapsed time in seconds for the download session
        """
        summary = self.get_summary()
        logger.info(Messages.Stats.HEADER)
        logger.info(Messages.Stats.TITLE())
        logger.info(Messages.Stats.PROCESSED(**summary))
        logger.info(Messages.Stats.SUCCESSFUL(**summary))
        logger.info(Messages.Stats.SKIPPED(**summary))
        logger.info(Messages.Stats.FAILED(**summary))
        logger.info(Messages.Stats.ELAPSED(elapsed=elapsed))
        logger.info(Messages.Stats.FOOTER)
