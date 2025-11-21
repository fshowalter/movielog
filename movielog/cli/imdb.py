from movielog.cli import radio_list
from movielog.repository import api as repository_api


def prompt() -> None:
    options = [
        (
            repository_api.update_datasets,
            "Update <cyan>ratings</cyan> data (via <cyan>dataset</cyan>).",
        ),
        (
            repository_api.update_title_data,
            "Update <cyan>title</cyan> data (via <cyan>pages</cyan>).",
        ),
        (
            repository_api.update_watchlist_credits,
            "Update <cyan>watchlist titles</cyan> for <cyan>directors</cyan>, <cyan>performers</cyan>, and <cyan>writers</cyan>.",  # noqa: E501
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
