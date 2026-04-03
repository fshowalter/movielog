from movielog.cli import ask_for_token
from movielog.exports import api as exports_api


def prompt() -> None:
    token = ask_for_token.prompt()

    if token is not None:
        exports_api.export_data(token)
