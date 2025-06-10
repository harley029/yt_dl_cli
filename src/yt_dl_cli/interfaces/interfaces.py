"""
Protocol interfaces for dependency injection and abstraction.

This module defines Protocol classes that establish contracts for various
components used throughout the application. These protocols enable loose
coupling, easier testing through mock implementations, and flexible
architecture by defining clear interfaces without concrete implementations.

The protocols follow the Dependency Inversion Principle, allowing high-level
modules to depend on abstractions rather than concrete implementations.
"""

from typing import Protocol, Any
from pathlib import Path


class ILogger(Protocol):
    """
    Protocol defining the interface for logger objects.

    This protocol ensures that any logger implementation provides the necessary
    logging methods with consistent signatures for dependency injection. It
    abstracts the logging functionality to allow for different logging backends
    (standard library logging, custom loggers, or mock loggers for testing).

    The protocol supports the standard logging levels and accepts flexible
    arguments to accommodate various logging patterns including string formatting,
    structured logging, and additional context via keyword arguments.

    Methods should follow standard logging conventions where higher-level
    methods (critical, error) typically indicate more severe issues than
    lower-level ones (info, warning).
    """

    def info(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """
        Log an informational message.

        Used for general information about program execution flow,
        successful operations, or non-critical status updates.

        Args:
            msg (Any): The message to log. Can be a string with format
                placeholders or any object with a string representation.
            *args (Any): Positional arguments for string formatting,
                following Python's % formatting convention.
            **kwargs (Any): Additional keyword arguments that may be
                used by specific logger implementations (e.g., extra
                context, stack info, etc.).

        Returns:
            None
        """

    def warning(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """
        Log a warning message.

        Used for potentially problematic situations that don't prevent
        the program from continuing but may indicate issues that should
        be addressed or monitored.

        Args:
            msg (Any): The warning message to log. Can be a string with
                format placeholders or any object with a string representation.
            *args (Any): Positional arguments for string formatting,
                following Python's % formatting convention.
            **kwargs (Any): Additional keyword arguments for logger-specific
                features like stack traces or contextual information.

        Returns:
            None
        """

    def error(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """
        Log an error message.

        Used for error conditions that prevented a specific operation
        from completing successfully but don't necessarily terminate
        the entire program.

        Args:
            msg (Any): The error message to log. Can be a string with
                format placeholders or any object with a string representation.
            *args (Any): Positional arguments for string formatting,
                following Python's % formatting convention.
            **kwargs (Any): Additional keyword arguments such as exc_info
                for exception details or stack_info for call stack.

        Returns:
            None
        """

    def critical(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """
        Log a critical error message.

        Used for very serious error conditions that may cause the
        program to terminate or indicate system-level failures that
        require immediate attention.

        Args:
            msg (Any): The critical error message to log. Can be a string
                with format placeholders or any object with a string representation.
            *args (Any): Positional arguments for string formatting,
                following Python's % formatting convention.
            **kwargs (Any): Additional keyword arguments for detailed
                error reporting, stack traces, or system context.

        Returns:
            None
        """


class IStatsCollector(Protocol):
    """
    Protocol defining the interface for statistics collection.

    This protocol ensures consistent statistics tracking across different
    implementations, allowing for easy testing and alternative stat collectors.
    It provides a simple interface for recording different types of operations
    and generating summary reports.

    Implementations should maintain internal counters for each type of recorded
    event and provide meaningful statistics through the report method. The
    protocol is designed to be thread-safe in implementations where concurrent
    access is expected.

    The statistics collected can be used for monitoring application performance,
    generating user feedback, debugging issues, or creating audit trails.
    """

    def record_success(self) -> None:
        """
        Record a successful operation.

        This method should be called whenever an operation (such as a download,
        file processing, or data transformation) completes successfully without
        errors. Implementations should increment their success counter and may
        also record additional metadata like timestamps or operation details.

        Returns:
            None
        """

    def record_failure(self) -> None:
        """
        Record a failed operation.

        This method should be called whenever an operation fails due to errors,
        exceptions, or other issues that prevent successful completion.
        Implementations should increment their failure counter and may store
        additional context about the failure type or cause.

        Returns:
            None
        """

    def record_skip(self) -> None:
        """
        Record a skipped operation.

        This method should be called when an operation is intentionally skipped
        rather than attempted. Common reasons include: file already exists,
        operation not needed due to current state, or user-defined filtering
        rules that exclude the operation.

        Skipped operations are distinct from failures as they represent
        intentional non-execution rather than failed attempts.

        Returns:
            None
        """

    def report(self, logger: ILogger, elapsed: float) -> None:
        """
        Generate and log a comprehensive summary report of collected statistics.

        This method should compile all recorded statistics into a human-readable
        summary and output it using the provided logger. The report typically
        includes counts for each operation type, percentages, rates, and timing
        information.

        Args:
            logger (ILogger): The logger instance to use for outputting the
                statistics report. Should typically use info level for
                normal reporting.
            elapsed (float): The total elapsed time in seconds for the
                operations being reported. Used to calculate rates and
                performance metrics.

        Returns:
            None
        """


class IFileChecker(Protocol):
    """
    Protocol defining the interface for file system operations.

    This abstraction allows for easy testing and alternative file system
    implementations while maintaining a consistent interface. It provides
    a minimal contract for file existence checking, which is commonly needed
    for validation, conditional processing, and avoiding duplicate operations.

    Implementations can range from direct file system access to mock
    implementations for testing, remote file system adapters, or cached
    implementations that optimize repeated checks.

    The protocol focuses on existence checking as this is often the primary
    file system query needed in download managers, file processors, and
    similar applications.
    """

    def exists(self, filepath: Path) -> bool:
        """
        Check if a file exists at the given path.

        This method should return True if a regular file exists at the
        specified path, and False otherwise. The behavior for directories,
        symbolic links, or other file system objects is implementation-defined
        but should be documented clearly.

        Implementations should handle edge cases gracefully, such as:
        - Permission denied errors (typically return False)
        - Network timeouts for remote file systems
        - Invalid path formats
        - Non-existent parent directories

        Args:
            filepath (Path): A Path object representing the file location
                to check. Should be an absolute or relative path that can
                be resolved by the underlying file system implementation.

        Returns:
            bool: True if the file exists and is accessible, False otherwise.
                Does not distinguish between "file doesn't exist" and
                "file exists but is not accessible".
        """
        ...
