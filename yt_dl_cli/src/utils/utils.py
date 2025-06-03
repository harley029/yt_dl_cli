from pathlib import Path
import re


class FileSystemChecker:
    """
    File system operations wrapper for checking file existence.

    This class provides an abstraction layer over file system operations,
    making the code more testable and allowing for alternative implementations.
    """

    def exists(self, filepath: Path) -> bool:
        """
        Check if a file exists at the specified path.

        Args:
            filepath (Path): Path to check for file existence

        Returns:
            bool: True if file exists, False otherwise
        """
        return filepath.exists()


class FilenameSanitizer:
    """
    Utility class for sanitizing filenames to ensure file system compatibility.

    This class handles the conversion of video titles and other strings into
    safe filenames that work across different operating systems.
    """

    @staticmethod
    def sanitize(name: str, max_length: int = 100) -> str:
        """
        Sanitize a string to make it safe for use as a filename.

        Removes or replaces characters that are invalid in filenames on most
        operating systems, and truncates the result to a maximum length.

        Args:
            name (str): Original string to sanitize
            max_length (int, optional): Maximum length of resulting filename. Defaults to 100.

        Returns:
            str: Sanitized filename safe for file system use

        Note:
            Invalid characters (<>:"/\\|?*) are replaced with underscores,
            and the result is trimmed of leading/trailing whitespace.
        """
        safe = re.sub(r'[<>:"/\\|?*]', "_", name)
        return safe[:max_length].strip()
