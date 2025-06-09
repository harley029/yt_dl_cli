"""
Internationalization (i18n) utilities for application localization.

This module provides a simple interface for setting up GNU gettext-based
internationalization in Python applications. It automatically detects the
system locale, searches for translation files in common directory structures,
and gracefully falls back to English when translations are unavailable.

The module is designed to work with standard GNU gettext .po/.mo file formats
and follows common localization directory conventions used in many open-source
projects.

Note:
    After calling setup_i18n(), the _() function becomes globally available
    for string translation throughout your application.
"""

import locale
import gettext
import os
from pathlib import Path
from typing import Optional

# Automatically search for locales directory near this file (or in package parent)
_this_dir = Path(__file__).resolve().parent
_locales_dirs = [
    _this_dir.parent / "locales",  # yt_dl_cli/locales
    _this_dir.parent.parent / "locales",  # if package is placed deeper
]


def get_system_lang() -> str:
    """
    Detect and return the system's default language code.

    This function attempts to determine the user's preferred language by
    examining the system locale settings. It extracts the language portion
    from the full locale string and returns a standardized 2-character
    language code.

    The function uses Python's built-in locale module to query the system's
    current locale configuration. If no locale is detected or an error occurs,
    it defaults to English ("en").

    Returns:
        str: A 2-character language code (ISO 639-1 format).
            Examples: "en" for English, "de" for German.
            Always returns "en" as fallback if system locale cannot be determined.

    Example:
        >>> get_system_lang()
        'en'

    Note:
        The function truncates longer locale strings to just the language code.
        For example, "en_US.UTF-8" becomes "en", "de_DE" becomes "de".
    """
    # Try environment variables first (most reliable for i18n!)
    for var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        lang = os.environ.get(var)
        if lang:
            # Extract first two letters (ISO 639-1), e.g. "de_DE.UTF-8" → "de"
            lang_code = lang.split("_")[0].split("-")[0].lower()
            if lang_code in ("en", "de", "uk", "ru"):
                return lang_code

    # Fallback to locale
    lang, _ = locale.getlocale()
    if lang:
        lang_code = lang[:2].lower()
        if lang_code in ("en", "de", "uk", "ru"):
            return lang_code
    return "en"


def setup_i18n(
    domain: str = "messages",
    localedir: Optional[str] = None,
    language: Optional[str] = None,
) -> None:
    """Set up internationalization (i18n) for the application.

    This function configures the GNU gettext internationalization system by:
    1. Detecting the system's default locale
    2. Loading the appropriate translation catalog
    3. Installing the translation function globally

    The function automatically falls back to English if the system locale
    cannot be determined or if translation files are not found.

    Args:
        domain (str, optional): The translation domain name, typically matching
            the base name of .po/.mo files. Defaults to "messages".
        localedir (str, optional): Directory path containing locale subdirectories
            with translation files. Expected structure:
            localedir/
            ├── en/
            │   └── LC_MESSAGES/
            │       ├── messages.po
            │       └── messages.mo
            └── ...
            Defaults to "locales".

    Returns:
        None: This function has no return value but installs translation
        functions globally, making _() function available for string translation.

    Raises:
        No exceptions are raised. If translation files are not found,
        the function gracefully falls back to installing a null translation
        that returns strings unchanged.

    Note:
        After calling this function, the _() function becomes globally available
        for translating strings. The detected language is truncated to a 2-character
        language code (e.g., "en_US" becomes "en") for compatibility with most
        translation file naming conventions.
    """
    # Determine language: provided or system default
    lang = (language or get_system_lang())[:2]

    # List of directories to search for translations
    search_dirs = [Path(localedir)] if localedir else _locales_dirs

    # Search for the first catalog with the required .mo file
    for dir_ in search_dirs:
        mo_file = dir_ / lang / "LC_MESSAGES" / f"{domain}.mo"
        if mo_file.exists():
            gettext.translation(domain, localedir=str(dir_), languages=[lang]).install()
            return

    # If translation not found — fallback to English (or original)
    gettext.install(domain)
