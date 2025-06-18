"""
Command line interface argument parsing module for the YouTube downloader CLI.

This module provides comprehensive command line argument parsing functionality
for the async video downloader application. It handles URL input from both
files and direct command line arguments, validates user input, and creates
properly configured application settings.

Key Features:
- Multiple URL input methods (file-based or direct CLI arguments)
- Configurable download directory and quality settings
- Concurrent download worker configuration
- Audio-only download option
- Robust error handling for file operations
- Comment and empty line filtering in URL files

The module integrates with the application's configuration system and
internationalization framework to provide a seamless user experience.

Example:
    Basic usage from command line:

    $ python -m yt_dl_cli -f urls.txt -d ./downloads -w 4 -q 720
    $ python -m yt_dl_cli --urls "https://youtube.com/watch?v=xyz" -a
    $ python -m yt_dl_cli --file links.txt --workers 3 --quality best

Dependencies:
    - argparse: Standard library argument parsing
    - pathlib: Cross-platform path handling
    - sys: System-specific parameters and functions
    - typing: Type hints for better code documentation
"""

import argparse
from pathlib import Path
import sys
from typing import List

from yt_dl_cli.config.config import Config
from yt_dl_cli.i18n.messages import Messages
from yt_dl_cli.utils.validators import ArgValidator


def parse_arguments() -> Config:
    """
    Parse command line arguments and create application configuration.

    This function handles all command line argument parsing and validation,
    including reading URLs from files or command line arguments. It provides
    comprehensive error handling for file operations and processes URL lists
    by filtering out comments and empty lines.

    The function creates an ArgumentParser instance, defines all supported
    command line options, parses the provided arguments, and then processes
    the URL input according to the specified method (file or direct URLs).
    Finally, it constructs and returns a fully populated Config object.

    Returns:
        Config: Fully populated configuration object containing all parsed
               settings ready for use by the download application. The Config
               object includes validated paths, worker counts, quality settings,
               and a cleaned list of URLs.

    Raises:
        SystemExit: Raised by argparse when invalid arguments are provided
                   or when --help is requested. This is standard argparse
                   behavior and should not be caught.

    Command Line Arguments:
        -f, --file (str): Path to file containing URLs, one per line.
                         Comments (lines starting with #) and empty lines
                         are automatically ignored. Default: "links.txt"

        -d, --dir (str): Target directory for downloaded files. Directory
                        will be created if it doesn't exist. Can be relative
                        or absolute path. Default: "downloads"

        -w, --workers (int): Maximum number of concurrent download workers.
                            Higher values may improve download speed but
                            consume more system resources. Default: 2

        -q, --quality (str): Preferred video quality for downloads.
                            Options: "best", "worst", "720", "480", "360"
                            Default: "best"

        -a, --audio-only (flag): When present, downloads only the audio
                                track instead of video. Useful for music
                                or podcast content.

        --urls (List[str]): Direct list of URLs to download. When provided,
                           this option overrides the --file option completely.
                           Multiple URLs can be specified separated by spaces.

    File Format:
        URL files should contain one URL per line. The following format
        is supported:

            # This is a comment line (ignored)
            https://youtube.com/watch?v=video1
            https://youtube.com/watch?v=video2

            # Empty lines above are also ignored
            https://youtube.com/watch?v=video3

    Error Handling:
        - FileNotFoundError: When the specified URL file doesn't exist,
          an error message is printed to stderr but execution continues
          with an empty URL list
        - Other file reading errors: Generic file reading errors are
          caught and reported with the specific error details
        - Invalid arguments: Handled by argparse with automatic help
          message display and program termination

    Example:
        >>> # Parse arguments from command line
        >>> config = parse_arguments()
        >>> print(f"Will download {len(config.urls)} videos")
        >>> print(f"Save directory: {config.save_dir}")
        >>> print(f"Quality: {config.quality}")
        >>> print(f"Workers: {config.max_workers}")

    Note:
        - URLs starting with '#' in files are treated as comments and ignored
        - Empty lines in URL files are automatically filtered out
        - Whitespace around URLs is automatically stripped
        - File reading errors are reported to stderr but don't crash the program
        - The --urls option completely overrides file-based URL input
        - Path objects are used for cross-platform compatibility
    """
    # Create the argument parser with descriptive help text
    parser = argparse.ArgumentParser(
        description="Async Video Downloader CLI",
        epilog="Use --help for detailed information about each option.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Define file input option
    parser.add_argument(
        "-f",
        "--file",
        default="links.txt",
        type=ArgValidator.validate_url_file,
        help="File with URLs (one per line, # for comments)",
    )

    # Define output directory option
    parser.add_argument(
        "-d",
        "--dir",
        default="downloads",
        type=ArgValidator.validate_directory,
        help="Save directory for downloaded files",
    )

    # Define worker thread configuration
    parser.add_argument(
        "-w",
        "--workers",
        type=ArgValidator.validate_workers,
        default=2,
        help="Maximum number of parallel downloads (default: 2)",
    )

    # Define quality selection option
    parser.add_argument(
        "-q",
        "--quality",
        choices=["best", "worst", "1080", "720", "480", "360"],
        type=ArgValidator.validate_quality,
        default="best",
        help="Video quality preference (default: best)",
    )

    # Define audio-only download flag
    parser.add_argument(
        "-a",
        "--audio-only",
        action="store_true",
        help="Download audio track only (no video)",
    )

    # Define direct URL input option
    parser.add_argument(
        "--urls", nargs="+", type=str, help="Direct URL list (overrides --file option)"
    )

    # Parse the command line arguments
    args = parser.parse_args()

    # Initialize URL list
    urls: List[str] = []

    # Process URL input based on provided options
    if args.urls:
        # Use directly provided URLs
        urls = args.urls
    else:
        # Read URLs from file with comprehensive error handling
        try:
            file_path = Path(args.file)
            content = file_path.read_text(encoding="utf-8")
            urls = content.splitlines()
        except FileNotFoundError:
            # Handle missing file gracefully
            print(Messages.CLI.FILE_NOT_FOUND(file=args.file), file=sys.stderr)
        except PermissionError as e:
            print(
                Messages.CLI.FILE_READ_ERROR(
                    file=args.file, error=f"Permission denied: {e}"
                ),
                file=sys.stderr,
            )
        except UnicodeDecodeError as e:
            print(
                Messages.CLI.FILE_READ_ERROR(
                    file=args.file, error=f"Encoding error: {e}"
                ),
                file=sys.stderr,
            )
        except IsADirectoryError as e:
            print(
                Messages.CLI.FILE_READ_ERROR(
                    file=args.file, error=f"Is a directory: {e}"
                ),
                file=sys.stderr,
            )
        except OSError as e:
            print(
                Messages.CLI.FILE_READ_ERROR(file=args.file, error=f"OS error: {e}"),
                file=sys.stderr,
            )
        except ValueError as e:
            print(
                Messages.CLI.FILE_READ_ERROR(file=args.file, error=f"Value error: {e}"),
                file=sys.stderr,
            )
        except Exception as e:  # pylint: disable=W0718
            print(
                Messages.CLI.FILE_READ_ERROR(file=args.file, error=e),
                file=sys.stderr,
            )

    # Clean and filter the URL list
    # Remove empty lines, comments, and strip whitespace
    urls = [
        url.strip()
        for url in urls
        if url and url.strip() and not url.strip().startswith("#")
    ]

    # Create and return the configuration object
    return Config(
        save_dir=Path(args.dir),
        max_workers=args.workers,
        quality=args.quality,
        audio_only=args.audio_only,
        urls=urls,
    )
