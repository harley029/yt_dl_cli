"""
Validation functions for CLI arguments.

This module provides reusable validation logic for CLI arguments,
ensuring that provided values adhere to application requirements.
"""

from pathlib import Path
from typing import List
import argparse


class ArgValidator:
    @staticmethod
    def validate_workers(value: str) -> int:
        """Validate the number of worker threads."""
        try:
            workers = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"'{value}' is not a valid integer.")

        if workers < 1 or workers > 10:
            raise argparse.ArgumentTypeError("Workers must be between 1 and 10.")
        return workers

    @staticmethod
    def validate_directory(path_str: str) -> Path:
        """Validate that the directory is writable or can be created."""
        path = Path(path_str)
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise argparse.ArgumentTypeError(f"Invalid directory '{path_str}': {e}") from e
        if not path.is_dir() or not path.exists():
            raise argparse.ArgumentTypeError(f"Path '{path_str}' is not a valid directory.")
        return path

    @staticmethod
    def validate_quality(quality: str) -> str:
        """Validate video quality."""
        valid_qualities = ["best", "worst", "1080", "720", "480", "360"]
        if quality not in valid_qualities:
            raise argparse.ArgumentTypeError(
                f"Quality must be one of {valid_qualities}, got '{quality}'."
            )
        return quality

    @staticmethod
    def validate_url_list(urls: List[str]) -> List[str]:
        """Validate that URLs are properly formatted."""
        if not urls:
            raise argparse.ArgumentTypeError("URL list cannot be empty.")
        for url in urls:
            if not (url.startswith("http://") or url.startswith("https://")):
                raise argparse.ArgumentTypeError(
                    f"Invalid URL '{url}'. URLs must start with 'http://' or 'https://'."
                )
        return urls

    @staticmethod
    def validate_url_file(file_path: str) -> Path:
        """Validate URL file existence and readability."""
        path = Path(file_path)
        if not path.is_file():
            raise argparse.ArgumentTypeError(
                f"URL file '{file_path}' does not exist or is not a file."
            )
        if not path.stat().st_size > 0:
            raise argparse.ArgumentTypeError(f"URL file '{file_path}' is empty.")
        return path
