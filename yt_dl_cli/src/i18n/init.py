import locale
import gettext


def setup_i18n(domain: str = "messages", localedir: str = "locales") -> None:
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
    lang_tuple = locale.getdefaultlocale()
    lang = lang_tuple[0][:2] if lang_tuple and lang_tuple[0] else "en"

    try:
        trans = gettext.translation(
            domain=domain, localedir=localedir, languages=[lang]
        )
        trans.install()
    except FileNotFoundError:
        gettext.install(domain)
