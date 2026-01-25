from movielog.cli import (
    add_viewing,
    export_data,
    imdb,
    manage_collections,
    manage_watchlist,
    radio_list,
)
from movielog.utils.logging import logger


@logger.catch
def prompt() -> None:
    options = [
        (add_viewing.prompt, "<cyan>Add Viewing</cyan>"),
        (manage_watchlist.prompt, "<cyan>Manage Watchlist</cyan>"),
        (manage_collections.prompt, "<cyan>Manage Collections</cyan>"),
        (imdb.prompt, "<cyan>IMDb</cyan>"),
        (export_data.prompt, "<cyan>Export Data</cyan>"),
    ]

    option_function = radio_list.prompt(
        title="Movie DB options:", options=options, rprompt="ESC to exit"
    )
    if option_function:
        option_function()
        prompt()
