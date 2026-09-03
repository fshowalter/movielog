import contextlib

from movielog.cli import ask_for_token
from movielog.repository import api as repository_api
from movielog.repository import imdb_http


def prompt() -> None:
    with contextlib.suppress(imdb_http.TokenPromptCancelledError):
        repository_api.update_title_data(ask_for_token.prompt)
