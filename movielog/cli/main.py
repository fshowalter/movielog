from movielog.cli import (
    add_viewing,
    manage_watchlist,
    radio_list,
    update_imdb_data,
    update_viewings,
)
from movielog.logger import logger


@logger.catch
def prompt() -> None:
    options = [
        (add_viewing.prompt, "<cyan>Add Viewing</cyan>"),
        (manage_watchlist.prompt, "<cyan>Manage Watchlist</cyan>"),
        (update_imdb_data.prompt, "<cyan>Update IMDb data</cyan>"),
        (update_viewings.prompt, "<cyan>Update Viewings</cyan>"),
        (None, "Exit"),
    ]

    option_function = radio_list.prompt(title="Movie DB options:", options=options,)
    if option_function:
        option_function()
        prompt()
