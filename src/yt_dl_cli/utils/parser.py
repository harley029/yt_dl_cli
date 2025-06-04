import argparse
from pathlib import Path
import sys
from typing import List

from yt_dl_cli.config.config import Config
from yt_dl_cli.i18n.messages import Messages


def parse_arguments() -> Config:
    """
    Parse command line arguments and create application configuration.

    This function handles all command line argument parsing and validation,
    including reading URLs from files or command line arguments. It also
    handles file reading errors gracefully and filters out empty lines
    and comments from URL files.

    Returns:
        Config: Fully populated configuration object ready for use

    Command Line Arguments:
        -f, --file: File containing URLs (default: links.txt)
        -d, --dir: Download directory (default: downloads)
        -w, --workers: Number of concurrent workers (default: 2)
        -q, --quality: Video quality (best/worst/720/480/360, default: best)
        -a, --audio-only: Download audio only flag
        --urls: Direct URL list (overrides file option)

    Note:
        URLs starting with '#' are treated as comments and ignored.
        Empty lines in URL files are automatically filtered out.
        File reading errors are reported to stderr but don't crash the program.
    """
    parser = argparse.ArgumentParser(description="Async Video Downloader CLI")
    parser.add_argument("-f", "--file", default="links.txt", help="File with URLs")
    parser.add_argument("-d", "--dir", default="downloads", help="Save directory")
    parser.add_argument(
        "-w", "--workers", type=int, default=2, help="Max parallel downloads"
    )
    parser.add_argument(
        "-q",
        "--quality",
        choices=["best", "worst", "720", "480", "360"],
        default="best",
        help="Video quality",
    )
    parser.add_argument("-a", "--audio-only", action="store_true", help="Audio only")
    parser.add_argument("--urls", nargs="+", help="List of URLs (overrides file)")

    args = parser.parse_args()
    urls: List[str] = []
    if args.urls:
        urls = args.urls
    else:
        try:
            content = Path(args.file).read_text(encoding="utf-8")
            urls = content.splitlines()
        except FileNotFoundError:
            print(Messages.CLI.FILE_NOT_FOUND(file=args.file), file=sys.stderr)
        except Exception as e:
            print(
                Messages.CLI.FILE_READ_ERROR(file=args.file, error=e),
                file=sys.stderr,
            )

    # Filter out empty/comment lines
    urls = [u.strip() for u in urls if u and not u.startswith("#")]
    return Config(
        save_dir=Path(args.dir),
        max_workers=args.workers,
        quality=args.quality,
        audio_only=args.audio_only,
        urls=urls,
    )
