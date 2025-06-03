from gettext import gettext as _


class Messages:
    """
    Container for all user-facing messages in the application.

    Messages are grouped by component for easy localization.
    """

    class Config:
        """Messages for configuration validation errors."""

        INVALID_WORKERS = _("max_workers must be at least 1, got {workers}")
        INVALID_QUALITY = _("quality must be one of: {valid}, got {quality}")
        # INVALID_WORKERS = "WRONG_NUMBERS_OF_WORKERS"
        # INVALID_QUALITY = "WRONG_QUALITY"

    class Core:
        """Messages used by the core downloader component."""

        SKIP_EXISTS = _("[SKIP] Already exists: {title}")
        START_DOWNLOAD = _("[START] {title}")
        DONE_DOWNLOAD = _("[DONE] {title}")
        ERROR_RESOURCE_CLOSE = _("Error closing resource: {error}")
        # SKIP_EXISTS = "FILE_ALREADY_EXISTS"
        # START_DOWNLOAD = "STARTED_DOWNLOAD"
        # DONE_DOWNLOAD = "DOWNLOAD_DONE"
        # ERROR_RESOURCE_CLOSE = "ERROR_CLOSING_RESOURCE"

    class Extractor:
        """Messages used by the video extracor component."""

        ERROR_EXTRACT = _("Failed to extract info for {url}: {error}")
        ERROR_NO_INFO = _("Unable to extract video info")
        # ERROR_EXTRACT = "INFO_EXTRACTION_ERROR"
        # ERROR_NO_INFO = "UNAVAILABLE_VIDEO_INFO"

    class Executor:
        """Messages used by the download executor component."""

        ERROR_DOWNLOAD = _("Download failed for {url}: {error}")
        # ERROR_DOWNLOAD = "DOWNLOAD_FAILED"

    class Stats:
        """Messages used for statistics reporting."""

        HEADER = "=" * 40
        TITLE = _("DOWNLOAD SUMMARY:")
        PROCESSED = _("Processed:    {total}")
        SUCCESSFUL = _("  Successful: {success}")
        SKIPPED = _("  Skipped:    {skipped}")
        FAILED = _("  Failed:     {failed}")
        ELAPSED = _("Elapsed time: {elapsed:.2f}s")
        FOOTER = "=" * 40
        # HEADER = "=" * 40
        # TITLE = "DOWNLOAD_SUMMARY"
        # PROCESSED = "PROCESSED"
        # SUCCESSFUL = "SUCCESSFUL"
        # SKIPPED = "SKIPPED"
        # FAILED = "FAILED"
        # ELAPSED = "ELAPSED_TIME"
        # FOOTER = "=" * 40

    class Orchestrator:
        """Messages used by the async orchestrator."""

        NO_URLS = _("No URLs to download.")
        STARTING = _("Starting download of {count} items with {workers} workers")

    class CLI:
        """Messages used in the command-line interface."""

        FILE_NOT_FOUND = _("Error: file '{file}' not found")
        FILE_READ_ERROR = _("Error reading '{file}': {error}")
        USER_INTERRUPT = _("Download interrupted by user.")
        CRITICAL_ERROR = _("Critical error: {error}")
