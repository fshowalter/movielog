from movielog.cli import radio_list
from movielog.repository import api as repository_api


def prompt() -> None:
    options = [
        (repository_api.update_datasets, "<cyan>Update datasets.</cyan>"),
        (
            repository_api.update_title_data,
            "<cyan>Update title cast, genres, and countries.</cyan>",
        ),
        (
            repository_api.update_watchlist_credits,
            "<cyan>Update watchlist director, performer, and writer credits.</cyan>",
        ),
    ]

    option_function = radio_list.prompt(
        title="IMDb:",
        options=options,
    )

    option_function()
    prompt()
