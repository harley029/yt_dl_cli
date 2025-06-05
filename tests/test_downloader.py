from yt_dl_cli.config.config import Config
from yt_dl_cli.core.downloader import VideoDownloader


def test_downloader_calls_yt_dlp_with_correct_params(mocker):
    """
    Проверяет, что VideoDownloader вызывает yt-dlp с правильными параметрами.
    mocker - это фикстура из pytest-mock.
    """
    # 1. Создаем мок (имитацию) для класса YoutubeDL из библиотеки yt_dlp
    # Мы перехватываем его до того, как он будет импортирован в нашем коде.
    mock_youtube_dl = mocker.patch("yt_dlp.YoutubeDL")

    # Создаем экземпляр мока, который будет возвращаться при вызове YoutubeDL()
    mock_instance = mock_youtube_dl.return_value

    # 2. Готовим конфигурацию для теста
    test_urls = ["url1", "url2"]
    config = Config(
        urls=test_urls, save_dir="test_dir", quality="1080", audio_only=False
    )

    # 3. Запускаем наш код
    downloader = VideoDownloader(config=config)
    downloader.download()

    # 4. Проверяем, что наш код вел себя как ожидалось

    # Проверяем, что YoutubeDL был инициализирован с правильными опциями
    mock_youtube_dl.assert_called_once()
    called_args, called_kwargs = mock_youtube_dl.call_args
    assert "outtmpl" in called_kwargs["params"]
    assert (
        called_kwargs["params"]["format"]
        == "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    )

    # Проверяем, что метод download был вызван с нашими URL
    mock_instance.download.assert_called_once_with(test_urls)


def test_downloader_audio_only_format(mocker):
    """
    Проверяет, что для --audio-only используется правильный формат.
    """
    mock_youtube_dl = mocker.patch("yt_dlp.YoutubeDL")

    config = Config(urls=["some_url"], audio_only=True)

    downloader = VideoDownloader(config=config)

    # Проверяем, что YoutubeDL был вызван с опциями для аудио
    called_args, called_kwargs = mock_youtube_dl.call_args
    assert called_kwargs["params"]["format"] == "bestaudio/best"
    assert called_kwargs["params"]["postprocessors"][0]["key"] == "FFmpegExtractAudio"
