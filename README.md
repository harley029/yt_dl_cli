# yt-dl-cli

[![codecov](https://codecov.io/gh/harley029/yt_dl_cli/graph/badge.svg?token=NldUlxhISV)](https://codecov.io/gh/harley029/yt_dl_cli)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=harley029_yt_dl_cli\&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=harley029_yt_dl_cli)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/d93d2765d003461683d7390a05c78beb)](https://app.codacy.com/gh/harley029/yt_dl_cli/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![GitHub release](https://img.shields.io/github/v/release/harley029/yt_dl_cli)
![Repo Size](https://img.shields.io/github/repo-size/harley029/yt_dl_cli)
[![PyPI version](https://img.shields.io/pypi/v/yt_dl_cli.svg)](https://pypi.org/project/yt_dl_cli/)
[![PyPI downloads](https://img.shields.io/pypi/dm/yt_dl_cli)](https://pypi.org/project/yt-dl-cli/)
[![Build Status](https://github.com/harley029/yt_dl_cli/actions/workflows/tests.yml/badge.svg)](https://github.com/harley029/yt_dl_cli/actions)
[![Pylint](https://img.shields.io/badge/lint-pylint-brightgreen)](https://github.com/harley029/yt_dl_cli/actions/workflows/tests.yml)
[![Flake8](https://img.shields.io/badge/lint-flake8-blue)](https://github.com/harley029/yt_dl_cli/actions/workflows/tests.yml)
[![mypy](https://img.shields.io/badge/type%20check-mypy-purple)](https://github.com/harley029/yt_dl_cli/actions/workflows/tests.yml)

🎥 **yt-dl-cli** is a command-line YouTube video downloader built with [yt-dlp](https://github.com/yt-dlp/yt-dlp), enhanced with internationalization (i18n), logging, and a modular, easily extensible architecture.

## Features

* Download videos from YouTube, Vimeo, Dailymotion, and other platforms supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp#supported-sites).
* Internationalized messages in English, German, Ukrainian, and Russian.
* Flexible command-line interface with customizable configuration.
* Robust error handling and comprehensive logging.
* Supports concurrent downloads to improve performance.
* Easy use for development.

## Documentation

Full documentation is available at:  
[https://harley029.github.io/yt_dl_cli/](https://harley029.github.io/yt_dl_cli/)

You can always find API reference, usage guides, and examples there.

## Architecture and Design

The video downloader is built around the principle of single responsibility, with each class handling a specific aspect of the download process. This design promotes testability, maintainability, and allows for easy extension and modification of individual components.

### Architecture Overview

The module implements a layered architecture with clear separation between:

1. **Information Layer** (`VideoInfoExtractor`):
   * Extracts video metadata without downloading content.
   * Validates video availability and accessibility.
   * Retrieves video information for processing decisions.

2. **Execution Layer** (`DownloadExecutor`):
   * Handles actual download operations.
   * Manages interactions and configurations with `yt-dlp`.
   * Provides robust error handling for download failures.

3. **Orchestration Layer** (`DownloaderCore`):
   * Coordinates the complete download workflow.
   * Integrates all components and manages dependencies.
   * Ensures proper resource lifecycle management and cleanup.
   * Manages file system operations and maintains download statistics.

### Key Components

* `VideoInfoExtractor`: Metadata extraction and validation.
* `DownloadExecutor`: Core download execution engine.
* `DownloaderCore`: Main orchestrator and workflow manager.

### Design Patterns

The architecture utilizes several well-known design patterns:

* **Strategy Pattern**: Format selection through `IFormatStrategy` interface.
* **Dependency Injection**: All dependencies injected through constructor parameters.
* **Context Manager**: Resource management implemented using `__enter__` and `__exit__` methods.
* **Facade Pattern**: `DownloaderCore` provides a simplified interface to complex operations.
* **Template Method**: Standardized download workflow with extensible, customizable steps.

### Error Handling Philosophy

The module emphasizes defensive programming practices:

* External API calls wrapped in try-catch blocks.
* Errors logged comprehensively without crashing the application.
* Graceful handling and logging of individual download failures.
* Resource cleanup guaranteed through context managers.
* Detailed error messages for easy troubleshooting and debugging.

### Performance Considerations

* Efficient metadata extraction without unnecessary downloads.
* File existence checking to avoid redundant operations.
* Resource pooling and cleanup to prevent memory leaks.
* Asynchronous design for concurrent operations.
* Minimal I/O operations through intelligent caching strategies.

### Integration Points

The module integrates smoothly with several external systems:

* **yt-dlp**: Core download engine and interface to video platforms.
* **File System**: Abstracted through `IFileChecker` interface.
* **Logging**: Managed through `ILogger` interface for monitoring and debugging.
* **Statistics**: Download progress tracking via `IStatsCollector`.
* **Configuration**: User preferences and settings via `Config` class.
* **Internationalization (i18n)**: Localized user feedback through `Messages`.

### Usage Patterns

The module supports multiple usage scenarios:

1. **Single Download Operations**:
   * Extract video information.
   * Check file existence.
   * Execute download if necessary.
   * Update statistics and logs.

2. **Batch Download Operations**:
   * Concurrent processing of multiple URLs.
   * Aggregate and track statistics across operations.
   * Graceful handling of individual download failures.

### Security Considerations

* Robust input validation for URLs and file paths.
* Safe filename sanitization to prevent directory traversal attacks.
* Secure handling of temporary files and downloaded content.
* Validation and sanitization of video metadata.
* Protection mechanisms against malicious URLs and potentially harmful content.

### Thread Safety

* `VideoInfoExtractor`: Thread-safe; each instance creates isolated yt-dlp sessions.
* `DownloadExecutor`: Thread-safe; each operation is isolated.
* `DownloaderCore`: Not thread-safe; designed to operate within single-thread contexts.
* Resource Management: Requires careful handling and coordination in multi-threaded environments.

## Installation

The package requires **Python 3.8** or newer.

The project is actively developed and tested on Python **3.12**, so using this version is recommended for maximum stability.
Install from PyPI:

```bash
pip install yt_dl_cli
```

## Dependencies

* **yt-dlp** – Core library for downloading videos.
* **colorama** – Terminal text styling and coloring.

## Usage

### Command-line interface

```bash
yt-dl-cli --urls https://www.youtube.com/watch?v=dQw4w9WgXcQ --quality 720 --dir videos
```

### Available CLI Options

| Option               | Description                              | Example Value          |
|----------------------|------------------------------------------|------------------------|
| `-f`, `--file`       | File containing URLs (one per line)      | `links.txt`            |
| `-d`, `--dir`        | Directory to save downloaded files       | `my_videos`            |
| `-w`, `--workers`    | Number of concurrent download workers    | `4`                    |
| `-q`, `--quality`    | Video quality preference                 | `best`, `720`, `480`   |
| `-a`, `--audio-only` | Download audio only                      | (flag)                 |
| `--urls`             | URLs provided directly via CLI           | `<YouTube URL>`        |

Example:

```bash
yt-dl-cli -f links.txt -d my_videos -w 4 -q best
```

## Testing & Code Coverage

Automated tests and code coverage are set up to ensure yt-dl-cli is stable and reliable.
All main modules are covered by unit tests.

### Run Tests Locally

Run the test suite using [pytest](https://docs.pytest.org):

```bash
pytest tests/ -v
```

Or with coverage report:

```bash
pytest --cov=yt_dl_cli --cov-report=html
```

After running with coverage, an HTML report will be generated in the htmlcov/ folder.

### View Coverage Locally

Open the generated report with:

```bash
python -m webbrowser htmlcov/index.html
```

### Continuous Integration

* All tests are automatically run on each push and pull request to the main branch.
* Coverage results are uploaded to [odecov](https://app.codecov.io/gh/harley029/yt_dl_cli) for tracking and reporting.
* You can check the current coverage status using the badge at the top of this [README](https://github.com/harley029/yt_dl_cli/blob/main/README.md).

## Usage as a Python module/API usuge

You can integrate **yt-dl-cli** directly into your Python scripts or applications

### Basic Usage

```python
from yt_dl_cli.main import VideoDownloader

# Initialize downloader with default settings (links are in links.txt)
downloader = VideoDownloader()
downloader.download()
```

### Custom Configuration

```python
from yt_dl_cli.main import VideoDownloader
from yt_dl_cli.config.config import Config
import logging

# Define custom configuration
config = Config(
    save_dir="my_videos",
    quality="720",
    max_workers=4,
    audio_only=False,
    urls=["https://example.com/video1", "https://example.com/video2"]
)

# Initialize downloader with custom settings
downloader = VideoDownloader(config=config)
downloader.download()
```

## Internationalization

The tool automatically detects your system locale, but you can explicitly set the language from **English**, **German**, **Ukrainian**, **Russian**:

```bash
export LANGUAGE=de  # German language
```

or in Python:

```python
from yt_dl_cli.main import VideoDownloader
from yt_dl_cli.i18n.init import setup_i18n

# Set up Ukrainian language
setup_i18n(language="uk")

# Initialize downloader and call download method
downloader = VideoDownloader()
downloader.download()
```

## Project Structure

```bash
yt_dl_cli/
├── src/
│   └── yt_dl_cli/
│       ├── config/
│       ├── core/
│       ├── i18n/
│       ├── interfaces/
│       ├── scripts/
│       ├── utils/
│       └── locales/
│
├── LICENSE
├── pyproject.toml
└── README.md
```

## Contributing

Feel free to open issues or pull requests to contribute to the development and improvement of **yt-dl-cli**.

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.
