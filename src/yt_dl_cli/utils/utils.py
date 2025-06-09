"""
File system utilities module for safe filename handling and file operations.

This module provides utilities for checking file existence and sanitizing
filenames to ensure compatibility across different operating systems.
The module includes two main classes:

- FileSystemChecker: Wrapper for file system operations
- FilenameSanitizer: Utility for sanitizing strings into safe filenames

The module is designed with testability in mind, providing abstractions
that allow for easy mocking and alternative implementations.

Example:
    Basic usage of the file system utilities:

    >>> from pathlib import Path
    >>> checker = FileSystemChecker()
    >>> sanitizer = FilenameSanitizer()
    >>>
    >>> # Check if a file exists
    >>> file_path = Path("example.txt")
    >>> if checker.exists(file_path):
    ...     print("File exists")
    >>>
    >>> # Sanitize a filename
    >>> safe_name = sanitizer.sanitize("Video: Title with <special> chars!")
    >>> print(safe_name)  # "Video_ Title with _special_ chars!"
"""

from pathlib import Path
import re


class FileSystemChecker:
    """
    File system operations wrapper for checking file existence.

    This class provides an abstraction layer over file system operations,
    making the code more testable and allowing for alternative implementations.
    It can be easily mocked or extended for different file system backends.

    Attributes:
        None

    Example:
        >>> checker = FileSystemChecker()
        >>> file_path = Path("my_file.txt")
        >>> if checker.exists(file_path):
        ...     print("File found!")
        ... else:
        ...     print("File not found.")
    """

    def exists(self, filepath: Path) -> bool:
        """
        Check if a file exists at the specified path.

        This method wraps the pathlib Path.exists() method to provide
        a consistent interface that can be easily mocked for testing
        or replaced with alternative implementations.

        Args:
            filepath (Path): Path object representing the file location
                           to check for existence

        Returns:
            bool: True if the file exists at the specified path,
                 False if the file does not exist or if there's an
                 error accessing the path

        Raises:
            OSError: May be raised if there are permission issues
                    accessing the file system (though this is rare
                    for existence checks)

        Example:
            >>> from pathlib import Path
            >>> checker = FileSystemChecker()
            >>> file_path = Path("/home/user/document.txt")
            >>> if checker.exists(file_path):
            ...     print("File is available")
            ... else:
            ...     print("File not found")
        """
        return filepath.exists()

    def is_dir(self, path):
        """
        Check if a path represents a directory (folder).

        This method determines whether the specified path points to a directory
        rather than a regular file or other filesystem object. It provides a
        consistent interface that can be easily mocked for testing purposes.

        The method handles both existing and non-existing paths gracefully:
        - For existing paths: returns True if it's a directory, False otherwise
        - For non-existing paths: returns False

        Args:
            path (str or Path): Path to check. Can be either a string path
                              or a pathlib.Path object. The path can be
                              absolute or relative to the current working
                              directory.

        Returns:
            bool: True if the path exists and is a directory,
                 False if the path doesn't exist, is a file,
                 or is another type of filesystem object

        Raises:
            OSError: May be raised if there are permission issues
                    accessing the path or its parent directory
            TypeError: If path cannot be converted to a Path object

        Example:
            >>> checker = FileSystemChecker()
            >>>
            >>> # Check existing directory
            >>> if checker.is_dir("/home/user/documents"):
            ...     print("It's a directory")
            >>>
            >>> # Check file (should return False)
            >>> if not checker.is_dir("/home/user/file.txt"):
            ...     print("It's not a directory")
            >>>
            >>> # Works with Path objects too
            >>> from pathlib import Path
            >>> dir_path = Path("./my_folder")
            >>> if checker.is_dir(dir_path):
            ...     print("Directory exists")
        """
        return Path(path).is_dir()

    def ensure_dir(self, path):
        """
        Create a directory and all necessary parent directories.

        This method ensures that a directory exists at the specified path,
        creating it along with any missing parent directories if needed.
        If the directory already exists, the method completes successfully
        without raising an error.

        This is equivalent to the Unix 'mkdir -p' command and is useful
        for preparing directory structures before file operations.

        Args:
            path (str or Path): Path where the directory should be created.
                              Can be either a string path or a pathlib.Path
                              object. The path can be absolute or relative
                              to the current working directory.

        Returns:
            None: This method doesn't return a value. Success is indicated
                 by the absence of exceptions.

        Raises:
            OSError: Raised if directory creation fails due to:
                    - Insufficient permissions
                    - Path conflicts (e.g., a file exists with the same name)
                    - Filesystem errors or limitations
            FileExistsError: Raised if the path exists but is not a directory
                           (e.g., it's a regular file)
            TypeError: If path cannot be converted to a Path object

        Example:
            >>> checker = FileSystemChecker()
            >>>
            >>> # Create a simple directory
            >>> checker.ensure_dir("new_folder")
            >>>
            >>> # Create nested directories
            >>> checker.ensure_dir("path/to/deep/folder")
            >>>
            >>> # Works with Path objects
            >>> from pathlib import Path
            >>> output_dir = Path("./output/results/data")
            >>> checker.ensure_dir(output_dir)
            >>>
            >>> # Safe to call multiple times
            >>> checker.ensure_dir("existing_folder")  # Won't raise error

        Note:
            - The method creates all missing parent directories automatically
            - If any part of the path already exists as a directory, it's preserved
            - The method is idempotent: calling it multiple times is safe
            - File permissions for created directories follow system defaults
            - On Windows, this handles long path names appropriately
        """
        Path(path).mkdir(parents=True, exist_ok=True)


class FilenameSanitizer:
    """
    Utility class for sanitizing filenames to ensure file system compatibility.

    This class handles the conversion of video titles and other strings into
    safe filenames that work across different operating systems including
    Windows, macOS, and Linux. It removes invalid characters and enforces
    length limits to prevent file system errors.

    The sanitizer handles common problematic characters found in user-generated
    content such as video titles, avoiding issues with file creation and
    manipulation across different platforms.

    Attributes:
        None (all methods are static)

    Example:
        >>> sanitizer = FilenameSanitizer()
        >>> title = 'My Video: "The Best" <Part 1>'
        >>> safe_title = sanitizer.sanitize(title)
        >>> print(safe_title)  # 'My Video_ _The Best_ _Part 1_'
    """

    @staticmethod
    def sanitize(name: str, max_length: int = 100) -> str:
        """
        Sanitize a string to make it safe for use as a filename.

        Removes or replaces characters that are invalid in filenames on most
        operating systems, and truncates the result to a maximum length.
        This method handles the most common problematic characters that
        cause issues across Windows, macOS, and Linux file systems.

        The following characters are replaced with underscores:
        - < > : " / \\ | ? *

        Args:
            name (str): Original string to sanitize. Can contain any
                       Unicode characters, though non-ASCII characters
                       may cause issues on some older file systems.
            max_length (int, optional): Maximum length of resulting filename.
                                      Defaults to 100 characters. Should be
                                      less than the file system's limit
                                      (typically 255 characters).

        Returns:
            str: Sanitized filename safe for file system use. The result
                will contain only characters that are safe across all
                major operating systems, with a length not exceeding
                the specified maximum.

        Raises:
            TypeError: If name is not a string or max_length is not an integer
            ValueError: If max_length is less than 1

        Example:
            >>> # Basic sanitization
            >>> FilenameSanitizer.sanitize('Video: "Title"')
            'Video_ _Title_'

            >>> # With custom length limit
            >>> long_title = "Very long video title that exceeds normal limits"
            >>> FilenameSanitizer.sanitize(long_title, max_length=20)
            'Very long video titl'

            >>> # Handling special characters
            >>> problematic = 'File<name>with:bad/chars\\and|more?stuff*'
            >>> FilenameSanitizer.sanitize(problematic)
            'File_name_with_bad_chars_and_more_stuff_'

        Note:
            - Invalid characters are replaced with underscores, not removed
            - Leading and trailing whitespace is stripped from the result
            - The method preserves the original string's case
            - Empty strings or strings with only invalid characters will
              result in a string of underscores
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not isinstance(max_length, int) or max_length < 1:
            raise ValueError("max_length must be a positive integer")

        safe = re.sub(r'[<>:"/\\|?*]', "_", name)
        return safe[:max_length].strip()
