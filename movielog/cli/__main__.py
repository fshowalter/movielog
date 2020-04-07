from typing import Any

from prompt_toolkit.formatted_text import HTML

from movielog.cli import (
    add_viewing,
    # manage_watchlist,
    update_imdb_data,
    # update_viewings,
)
from movielog.cli import radio_list
from movielog.logger import logger


@logger.catch
def prompt() -> Any:
    options = radio_list.CallableOptions(
        [
            (add_viewing.prompt, HTML("<cyan>Add Viewing</cyan>")),
            # (manage_watchlist.prompt, HTML("<cyan>Manage Watchlist</cyan>")),
            (update_imdb_data.prompt, HTML("<cyan>Update IMDb data</cyan>")),
            # (update_viewings.prompt, HTML("<cyan>Update Viewings</cyan>")),
            (None, "Exit"),
        ]
    )

    option_function = radio_list.prompt(title="Movie DB options:", options=options,)

    if option_function:
        option_function()
        prompt()


if __name__ == "__main__":
    prompt()
