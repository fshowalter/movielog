from typing import Any

from prompt_toolkit.formatted_text import HTML

from movie_db.cli import (
    _radio_list,
    add_viewing,
    manage_watchlist,
    update_imdb_data,
    update_viewings,
)
from movie_db.logger import logger


@logger.catch
def prompt() -> Any:
    options = _radio_list.CallableOptions([
        (add_viewing.prompt, HTML('<cyan>Add Viewing</cyan>')),
        (manage_watchlist.prompt, HTML('<cyan>Manage Watchlist</cyan>')),
        (update_imdb_data.prompt, HTML('<cyan>Update IMDb data</cyan>')),
        (update_viewings.prompt, HTML('<cyan>Update Viewings</cyan>')),
        (None, 'Exit'),
    ])

    option_function = _radio_list.prompt(
        title='Movie DB options:',
        options=options,
    )

    if option_function:
        option_function()
        prompt()
