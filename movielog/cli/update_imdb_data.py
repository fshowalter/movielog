from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import confirm

from movielog import imdb_s3_orchestrator
from movielog.cli import radio_list


def prompt() -> None:
    options = radio_list.CallableOptions(
        [
            (None, "Go back"),
            (update_imdb_s3_data, HTML("<cyan>Update datasets</cyan>")),
            # (update_imdb_web_data, HTML("<cyan>Update credits</cyan>")),
        ]
    )

    option_function = radio_list.prompt(title="Update IMDb data:", options=options,)

    if option_function:
        option_function()
        prompt()


def update_imdb_s3_data() -> None:
    if confirm("Download and update IMDb data from S3?"):
        imdb_s3_orchestrator.orchestrate_update()


# def update_imdb_web_data() -> None:
#     if confirm("Update watchlist credits with IMDb web data?"):
#         watchlist.update_titles_for_people()
