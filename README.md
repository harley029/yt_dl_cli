# yt-dl-cli

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=harley029_yt_dl_cli\&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=harley029_yt_dl_cli)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/d93d2765d003461683d7390a05c78beb)](https://app.codacy.com/gh/harley029/yt_dl_cli/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![GitHub release](https://img.shields.io/github/v/release/harley029/yt_dl_cli)
![Repo Size](https://img.shields.io/github/repo-size/harley029/yt_dl_cli)

🎥 **yt-dl-cli** is a command-line YouTube video downloader built with [yt-dlp](https://github.com/yt-dlp/yt-dlp), enhanced with internationalization (i18n), logging, and a modular, easily extensible architecture.

## Features

* Download videos from YouTube, Vimeo, Dailymotion, and other platforms supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp#supported-sites).
* Internationalized messages in English, German, Ukrainian, and Russian.
* Flexible command-line interface with customizable configuration.
* Robust error handling and comprehensive logging.
* Supports concurrent downloads to improve performance.
* Easy use for development.

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

## Usage in Python Projects

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
    urls=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
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

```
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
