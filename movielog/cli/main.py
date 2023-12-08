from movielog.cli import add_viewing, imdb, manage_watchlist, radio_list
from movielog.exports import api as exports_api
from movielog.utils.logging import logger


@logger.catch
def prompt() -> None:
    options = [
        (add_viewing.prompt, "<cyan>Add Viewing</cyan>"),
        (manage_watchlist.prompt, "<cyan>Manage Watchlist</cyan>"),
        (imdb.prompt, "<cyan>IMDb</cyan>"),
        (exports_api.export_data, "<cyan>Export Data</cyan>"),
    ]

    option_function = radio_list.prompt(
        title="Movie DB options:", options=options, rprompt="ESC to exit"
    )
    if option_function:
        option_function()
        prompt()
