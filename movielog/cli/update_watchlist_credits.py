import contextlib

from movielog.cli import ask_for_token
from movielog.repository import api as repository_api
from movielog.repository import imdb_http


def prompt() -> None:
    with contextlib.suppress(imdb_http.TokenPromptCancelledError):
        repository_api.update_watchlist_credits(ask_for_token.prompt)
