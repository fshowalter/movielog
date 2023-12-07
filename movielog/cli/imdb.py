from movielog.cli import radio_list
from movielog.repository import api as repository_api


def prompt() -> None:
    options = [
        (
            repository_api.update_datasets,
            "<cyan>Update dataset data (title, year, original title, runtime, and votes).</cyan>",
        ),
        (
            repository_api.update_title_data,
            "<cyan>Update page data (cast, genres, release date, and countries)</cyan>",
        ),
        (
            repository_api.update_watchlist_credits,
            "<cyan>Update titles for watchlist directors, performers, and writers.</cyan>",
        ),
        (
            repository_api.validate_data,
            "<cyan>Validate title data.</cyan>",
        ),
    ]

    option_function = radio_list.prompt(
        title="IMDb:",
        options=options,
    )

    if option_function:
        option_function()
        prompt()
