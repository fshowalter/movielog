from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import confirm

from movie_db import imdb_files, watchlist
from movie_db.cli import _radio_list


def prompt() -> None:
    options = _radio_list.CallableOptions([
        (None, 'Go back'),
        (update_imdb_s3_data, HTML('<cyan>Update datasets</cyan>')),
        (update_imdb_web_data, HTML('<cyan>Update credits</cyan>')),
    ])

    option_function = _radio_list.prompt(
        title='Update IMDb data:',
        options=options,
    )

    if option_function:
        option_function()
        prompt()


def update_imdb_s3_data() -> None:
    if confirm('Download and update IMDb data from S3?'):
        imdb_files.orchestrate_update()


def update_imdb_web_data() -> None:
    if confirm('Update watchlist credits with IMDb web data?'):
        watchlist.update_titles_for_people()
