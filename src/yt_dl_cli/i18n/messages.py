from gettext import gettext as _


class LazyTranslation:
    def __init__(self, template):
        self.template = template

    def __call__(self, **kwargs):
        import builtins

        _ = builtins.__dict__.get("_", lambda x: x)
        return _(self.template).format(**kwargs) if kwargs else _(self.template)

    def __str__(self):
        raise RuntimeError(
            "Do not use LazyTranslation objects directly! "
            "Call as a function, e.g. Messages.Stats.TITLE()"
        )


class Messages:
    """
    Container for all user-facing messages in the application.

    Messages are grouped by component for easy localization.
    """

    class Config:
        """Messages for configuration validation errors."""

        INVALID_WORKERS = LazyTranslation(
            "max_workers must be at least 1, got {workers}"
        )
        INVALID_QUALITY = LazyTranslation(
            "quality must be one of: {valid}, got {quality}"
        )

    class Core:
        """Messages used by the core downloader component."""

        SKIP_EXISTS = LazyTranslation("[SKIP] Already exists: {title}")
        START_DOWNLOAD = LazyTranslation("[START] {title}")
        DONE_DOWNLOAD = LazyTranslation("[DONE] {title}")
        ERROR_RESOURCE_CLOSE = LazyTranslation("Error closing resource: {error}")

    class Extractor:
        """Messages used by the video extracor component."""

        ERROR_EXTRACT = LazyTranslation("Failed to extract info for {url}: {error}")
        ERROR_NO_INFO = LazyTranslation("Unable to extract video info")

    class Executor:
        """Messages used by the download executor component."""

        ERROR_DOWNLOAD = LazyTranslation("Download failed for {url}: {error}")

    class Stats:
        """Messages used for statistics reporting."""

        HEADER = "=" * 40
        TITLE = LazyTranslation("DOWNLOAD SUMMARY:")
        PROCESSED = LazyTranslation("Processed:    {total}")
        SUCCESSFUL = LazyTranslation("  Successful: {success}")
        SKIPPED = LazyTranslation("  Skipped:    {skipped}")
        FAILED = LazyTranslation("  Failed:     {failed}")
        ELAPSED = LazyTranslation("Elapsed time: {elapsed:.2f}s")
        FOOTER = "=" * 40

    class Orchestrator:
        """Messages used by the async orchestrator."""

        NO_URLS = LazyTranslation("No URLs to download.")
        STARTING = LazyTranslation(
            "Starting download of {count} items with {workers} workers"
        )

    class CLI:
        """Messages used in the command-line interface."""

        FILE_NOT_FOUND = LazyTranslation("Error: file '{file}' not found")
        FILE_READ_ERROR = LazyTranslation("Error reading '{file}': {error}")
        USER_INTERRUPT = LazyTranslation("Download interrupted by user.")
        CRITICAL_ERROR = LazyTranslation("Critical error: {error}")
