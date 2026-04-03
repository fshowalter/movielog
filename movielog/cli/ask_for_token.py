from movielog.cli import ask

NEEDS_TOKEN = False


def prompt() -> str | None:
    if not NEEDS_TOKEN:
        return ""

    return ask.prompt("aws-waf-token: ")
