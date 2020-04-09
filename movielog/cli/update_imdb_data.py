from movielog import imdb_s3_orchestrator, watchlist
from movielog.cli import confirm, radio_list


def prompt() -> None:
    options = [
        (None, "Go back"),
        (update_imdb_s3_data, "<cyan>Update datasets</cyan>"),
        (update_imdb_web_data, "<cyan>Update credits</cyan>"),
    ]

    option_function = radio_list.prompt(title="Update IMDb data:", options=options)

    if option_function:
        option_function()
        prompt()


def update_imdb_s3_data() -> None:
    if confirm.prompt("<cyan>Download and update IMDb data</cyan> from S3?"):
        imdb_s3_orchestrator.orchestrate_update()


def update_imdb_web_data() -> None:
    prompt_text = (
        "Update <cyan>watchlist credits</cyan> with <cyan>IMDb web data</cyan>?"
    )
    if confirm.prompt(prompt_text):
        watchlist.update_watchlist_titles_table()
