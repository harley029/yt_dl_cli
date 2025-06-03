import locale
import gettext


def setup_i18n(domain: str = "messages", localedir: str = "locales") -> None:
    lang_tuple = locale.getdefaultlocale()
    lang = lang_tuple[0][:2] if lang_tuple and lang_tuple[0] else "en"

    try:
        trans = gettext.translation(
            domain=domain, localedir=localedir, languages=[lang]
        )
        trans.install()
    except FileNotFoundError:
        gettext.install(domain)