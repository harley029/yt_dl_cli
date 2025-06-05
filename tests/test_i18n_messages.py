import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from yt_dl_cli.i18n.messages import Messages


def test_messages_config():
    msg = Messages.Config.INVALID_WORKERS(workers=0)
    assert "must be at least" in msg
