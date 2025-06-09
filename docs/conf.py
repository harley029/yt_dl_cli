# Configuration file for the Sphinx documentation builder.

import os
import sys

# Добавляем src/ в PYTHONPATH, чтобы Sphinx видел пакеты как yt_dl_cli.*
sys.path.insert(0, os.path.abspath("../src"))

project = "YT-DL-CLI Video downloader"
copyright = "2025, Oleksandr Kharchenko"
author = "Oleksandr Kharchenko"

# Расширения Sphinx
extensions = [
    "sphinx.ext.autodoc",
]

# Пути для шаблонов
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Опции для автодока по умолчанию
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}


# Тема HTML
html_theme = "nature"
html_static_path = ["_static"]
def setup(app):
    """Customize Sphinx HTML theme"""
    app.add_css_file("custom.css")
