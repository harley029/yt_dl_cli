import logging
from pathlib import Path


class LoggerFactory:
    """
    Factory class for creating and configuring logger instances.

    This factory handles the setup of logging configuration including both
    console and file output, ensuring consistent logging behavior throughout
    the application.
    """

    @staticmethod
    def get_logger(save_dir: Path) -> logging.Logger:
        """
        Create and configure a logger instance with both console and file handlers.

        Sets up logging to output to both the console and a log file in the
        specified save directory. Creates the directory if it doesn't exist.

        Args:
            save_dir (Path): Directory where the log file will be created

        Returns:
            logging.Logger: Configured logger instance ready for use

        Note:
            Only configures the root logger once to avoid duplicate handlers
            in subsequent calls.
        """
        save_dir.mkdir(parents=True, exist_ok=True)
        root = logging.getLogger()
        if not root.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s",
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler(save_dir / "download.log", encoding="utf-8"),
                ],
            )
        return logging.getLogger("video_dl_cli")
