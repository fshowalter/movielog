from movielog.cli import ask


def prompt() -> str | None:
    return ask.prompt("aws-waf-token: ")
