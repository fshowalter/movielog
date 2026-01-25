from movielog.cli import radio_list, update_title_data, update_watchlist_credits, validate_data
from movielog.repository import api as repository_api


def prompt() -> None:
    options = [
        (
            repository_api.update_datasets,
            "Update <cyan>ratings</cyan> data (via <cyan>dataset</cyan>).",
        ),
        (
            update_title_data.prompt,
            "Update <cyan>title</cyan> data (via <cyan>pages</cyan>).",
        ),
        (
            update_watchlist_credits.prompt,
            "Update <cyan>watchlist titles</cyan> for <cyan>directors</cyan>, <cyan>performers</cyan>, and <cyan>writers</cyan>.",  # noqa: E501
        ),
        (
            validate_data.prompt,
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
