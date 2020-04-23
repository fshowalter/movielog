from movielog import imdb_s3_orchestrator
from movielog.cli import (
    add_viewing,
    confirm,
    manage_watchlist,
    radio_list,
    update_viewings,
)
from movielog.logger import logger


@logger.catch
def prompt() -> None:
    options = [
        (add_viewing.prompt, "<cyan>Add Viewing</cyan>"),
        (manage_watchlist.prompt, "<cyan>Manage Watchlist</cyan>"),
        (update_imdb_s3_data, "<cyan>Update IMDb data</cyan>"),
        (update_viewings.prompt, "<cyan>Update Viewings</cyan>"),
        (None, "Exit"),
    ]

    option_function = radio_list.prompt(title="Movie DB options:", options=options,)
    if option_function:
        option_function()
        prompt()


def update_imdb_s3_data() -> None:
    if confirm.prompt("<cyan>Download and update IMDb data?</cyan>"):
        imdb_s3_orchestrator.orchestrate_update()
