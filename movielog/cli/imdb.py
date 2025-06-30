from movielog.cli import radio_list
from movielog.repository import api as repository_api


def prompt() -> None:
    options = [
        (
            repository_api.update_datasets,
            "Update <cyan>dataset</cyan> data (<cyan>title</cyan>, <cyan>year</cyan>, <cyan>original title</cyan>, <cyan>runtime</cyan>, and <cyan>votes</cyan>).",  # noqa: E501
        ),
        (
            repository_api.update_title_data,
            "Update <cyan>page</cyan> data (<cyan>cast</cyan>, <cyan>genres</cyan>, <cyan>release date</cyan>, and <cyan>countries</cyan>).",  # noqa: E501
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
