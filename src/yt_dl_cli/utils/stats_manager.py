"""
Statistics Management Module

This module provides functionality for tracking and reporting download operation statistics.
It includes the StatsManager class which maintains counters for various download outcomes
and generates comprehensive reports with elapsed time information.

Classes:
    StatsManager: Main statistics tracking and reporting class

Dependencies:
    - dataclasses: For creating the dataclass structure
    - typing: For type hints
    - yt_dl_cli.interfaces.interfaces: For logger interface
    - yt_dl_cli.i18n.messages: For internationalized messages
"""

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
    It serves as a centralized point for collecting and reporting download
    session statistics including success rates, failures, and performance metrics.

    Attributes:
        success (int): Count of successful downloads. Defaults to 0.
        failed (int): Count of failed downloads. Defaults to 0.
        skipped (int): Count of skipped downloads (files already exist). Defaults to 0.

    Example:
        >>> stats = StatsManager()
        >>> stats.record_success()
        >>> stats.record_failure()
        >>> summary = stats.get_summary()
        >>> print(summary['total'])  # Output: 2
    """

    success: int = 0
    failed: int = 0
    skipped: int = 0

    def record_success(self) -> None:
        """
        Increment the success counter by one.

        This method should be called whenever a download operation
        completes successfully.
        """
        self.success += 1

    def record_failure(self) -> None:
        """
        Increment the failure counter by one.

        This method should be called whenever a download operation
        fails due to any error condition.
        """
        self.failed += 1

    def record_skip(self) -> None:
        """
        Increment the skip counter by one.

        This method should be called whenever a download operation
        is skipped, typically because the target file already exists.
        """
        self.skipped += 1

    def get_summary(self) -> Dict[str, int]:
        """
        Calculate and return a summary of all statistics.

        Computes the total count by summing all individual counters
        and returns a comprehensive dictionary with all statistics.

        Returns:
            Dict[str, int]: Dictionary containing the following keys:
                - 'success': Number of successful downloads
                - 'failed': Number of failed downloads
                - 'skipped': Number of skipped downloads
                - 'total': Total number of processed items

        Example:
            >>> stats = StatsManager()
            >>> stats.success = 5
            >>> stats.failed = 2
            >>> stats.skipped = 1
            >>> summary = stats.get_summary()
            >>> summary
            {'success': 5, 'failed': 2, 'skipped': 1, 'total': 8}
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
        and total elapsed time, formatted with visual separators for easy reading.
        The report includes header/footer formatting and uses internationalized
        messages for consistent presentation.

        Args:
            logger (ILogger): Logger instance to output the report. Must implement
                            the ILogger interface with an info() method.
            elapsed (float): Total elapsed time in seconds for the download session.
                           Should be a positive number representing the duration.

        Raises:
            AttributeError: If the logger doesn't implement the required interface.

        Example:
            >>> import time
            >>> from unittest.mock import Mock
            >>>
            >>> logger = Mock()
            >>> stats = StatsManager()
            >>> stats.success = 10
            >>> stats.failed = 2
            >>>
            >>> start_time = time.time()
            >>> # ... perform downloads ...
            >>> elapsed_time = time.time() - start_time
            >>>
            >>> stats.report(logger, elapsed_time)
            This will log a formatted report with all statistics
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
