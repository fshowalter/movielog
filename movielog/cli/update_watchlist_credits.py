from movielog.cli import ask_for_token
from movielog.repository import api as repository_api


def prompt() -> None:
    token = ask_for_token.prompt()

    if token:
        repository_api.update_watchlist_credits(token)
