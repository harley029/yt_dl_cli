from typing import Protocol, Any
from pathlib import Path


class ILogger(Protocol):
    """
    Protocol defining the interface for logger objects.

    This protocol ensures that any logger implementation provides the necessary
    logging methods with consistent signatures for dependency injection.
    """

    def info(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log an info-level message."""
        ...

    def warning(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log a warning-level message."""
        ...

    def error(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log an error-level message."""
        ...

    def critical(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log a critical-level message."""
        ...


class IStatsCollector(Protocol):
    """
    Protocol defining the interface for statistics collection.

    This protocol ensures consistent statistics tracking across different
    implementations, allowing for easy testing and alternative stat collectors.
    """

    def record_success(self) -> None:
        """Record a successful download operation."""
        ...

    def record_failure(self) -> None:
        """Record a failed download operation."""
        ...

    def record_skip(self) -> None:
        """Record a skipped download operation (e.g., file already exists)."""
        ...

    def report(self, logger: ILogger, elapsed: float) -> None:
        """Generate and log a summary report of all recorded statistics."""
        ...


class IFileChecker(Protocol):
    """
    Protocol defining the interface for file system operations.

    This abstraction allows for easy testing and alternative file system
    implementations while maintaining a consistent interface.
    """

    def exists(self, filepath: Path) -> bool:
        """Check if a file exists at the given path."""
        ...
