""" Tests global settings  """
import warnings
import pytest
from pathlib import Path

warnings.filterwarnings(
    "ignore", category=RuntimeWarning, message="coroutine '.*' was never awaited"
)

@pytest.fixture(autouse=True, scope="session")
def ensure_links_txt():
    path = Path("links.txt")
    if not path.exists():
        path.write_text("https://test.url/should/be/ignored\n")
    yield
    if path.exists():
        path.unlink()
