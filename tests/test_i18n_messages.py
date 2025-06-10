import builtins
import sys
import os

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from yt_dl_cli.i18n.init import get_system_lang, setup_i18n
from yt_dl_cli.i18n.messages import Messages


def test_messages_config():
    """ Testing of Messages.Config  """
    msg = Messages.Config.INVALID_WORKERS(workers=0)
    assert "must be at least" in msg


def test_lazy_translation_str_raises():
    """ Testing of lazy translation strings  """
    # Проверяем, что попытка str() вызывает RuntimeError
    lazy = Messages.Config.INVALID_WORKERS
    with pytest.raises(RuntimeError):
        str(lazy)


@pytest.mark.parametrize(
    "envvar,value,expected",
    [
        ("LANGUAGE", "en_US.UTF-8", "en"),
        ("LANGUAGE", "de_DE.UTF-8", "de"),
        ("LANGUAGE", "uk_UA.UTF-8", "uk"),
        ("LANGUAGE", "ru_RU.UTF-8", "ru"),
        ("LANG", "en_US.UTF-8", "en"),
        ("LANG", "de_DE.UTF-8", "de"),
        ("LANG", "uk_UA.UTF-8", "uk"),
        ("LANG", "ru_RU.UTF-8", "ru"),
        ("LC_ALL", "en_GB.UTF-8", "en"),
        ("LC_ALL", "de_DE.UTF-8", "de"),
        ("LC_ALL", "uk_UA.UTF-8", "uk"),
        ("LC_ALL", "ru_RU.UTF-8", "ru"),
        ("LC_MESSAGES", "en_US", "en"),
        ("LC_MESSAGES", "de_DE", "de"),
        ("LC_MESSAGES", "uk_UA", "uk"),
        ("LC_MESSAGES", "ru_RU", "ru"),
        ("LANGUAGE", "", "en"),  # пустое значение — default en
    ],
)
def test_get_system_lang(monkeypatch, envvar, value, expected):
    """ Test get_system_lang  """
    # Сбрасываем все возможные переменные окружения
    for var in ["LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"]:
        monkeypatch.delenv(var, raising=False)
    # Устанавливаем только нужную переменную
    if value:
        monkeypatch.setenv(envvar, value)
    else:
        monkeypatch.delenv(envvar, raising=False)

    lang = get_system_lang()
    assert lang == expected


def test_get_system_languages(monkeypatch):
    """ Test get_system_languages  """

    monkeypatch.setenv("LANGUAGE", "de_DE.UTF-8")
    assert get_system_lang() == "de"

    monkeypatch.setenv("LANGUAGE", "uk_UA.UTF-8")
    assert get_system_lang() == "uk"

    monkeypatch.setenv("LANGUAGE", "ru_RU.UTF-8")
    assert get_system_lang() == "ru"

    monkeypatch.setenv("LANGUAGE", "en_US.UTF-8")
    assert get_system_lang() == "en"


def test_get_system_lang_fallback_locale(monkeypatch):
    """ Test get_system_lang with fallback to locale.getlocale  """
    import locale
    from yt_dl_cli.i18n.init import get_system_lang

    # Удаляем все переменные окружения, которые может использовать функция
    for var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        monkeypatch.delenv(var, raising=False)

    # Мокаем locale.getlocale так, чтобы возвращалось "en_US"
    monkeypatch.setattr(locale, "getlocale", lambda: ("en_US", "UTF-8"))
    assert get_system_lang() == "en"

    # Мокаем locale.getlocale так, чтобы возвращалось "de_DE"
    monkeypatch.setattr(locale, "getlocale", lambda: ("de_DE", "UTF-8"))
    assert get_system_lang() == "de"

    # Мокаем locale.getlocale так, чтобы возвращалось None
    monkeypatch.setattr(locale, "getlocale", lambda: (None, None))
    assert get_system_lang() == "en"


def test_setup_i18n_fallback_to_gettext_install(monkeypatch):
    """ Test setup_i18n_fallback_to_gettext_install  """
    # 1. Мокаем gettext.translation чтобы всегда возвращать объект без install()
    class FakeTranslation:
        def install(self):
            raise AssertionError("Не должен быть вызван!")

    monkeypatch.setattr(
        "yt_dl_cli.i18n.init.gettext.translation", lambda *a, **kw: FakeTranslation()
    )

    # 2. Мокаем Path.exists чтобы всегда возвращать False (нет mo-файлов)
    monkeypatch.setattr("pathlib.Path.exists", lambda self: False)

    # 3. Мокаем gettext.install чтобы зафиксировать вызов
    called = {}

    def fake_install(domain, *a, **k):
        called["domain"] = domain
        builtins._ = lambda x: f"fallback:{x}"  # type: ignore

    monkeypatch.setattr("yt_dl_cli.i18n.init.gettext.install", fake_install)

    # 4. Запускаем setup_i18n — должен сработать fallback через gettext.install
    setup_i18n(language="en")
    assert hasattr(builtins, "_")
    assert builtins._("hello") == "fallback:hello"  # type: ignore
    assert called["domain"] == "messages"
