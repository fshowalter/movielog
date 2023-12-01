from movielog import api as movielog_api
from movielog.cli import add_viewing, confirm, imdb, manage_watchlist, radio_list
from movielog.exports import api as exports_api
from movielog.utils.logging import logger


@logger.catch
def prompt() -> None:
    options = [
        (add_viewing.prompt, "<cyan>Add Viewing</cyan>"),
        (manage_watchlist.prompt, "<cyan>Manage Watchlist</cyan>"),
        (imdb.prompt, "<cyan>IMDb</cyan>"),
        (export, "<cyan>Export Data</cyan>"),
        (exports_api.export_data, "Fix data"),
        (None, "Exit"),
    ]

    option_function = radio_list.prompt(
        title="Movie DB options:",
        options=options,
    )
    if option_function:
        option_function()
        prompt()


def export() -> None:
    prompt_text = "<cyan>Export review, viewing, watchlist, and stats data?</cyan>"
    if confirm.prompt(prompt_text):
        movielog_api.export_data()
