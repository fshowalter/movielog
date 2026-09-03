import contextlib

from movielog.cli import ask_for_token
from movielog.exports import api as exports_api
from movielog.repository import imdb_http


def prompt() -> None:
    with contextlib.suppress(imdb_http.TokenPromptCancelledError):
        exports_api.export_data(ask_for_token.prompt)
