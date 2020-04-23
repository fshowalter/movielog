from movielog import watchlist
from movielog.cli import (
    add_director,
    add_performer,
    add_to_collection,
    add_writer,
    confirm,
    new_collection,
    radio_list,
)


def prompt() -> None:
    options = [
        (None, "Go back"),
        (add_director.prompt, "<cyan>Add Director</cyan>"),
        (add_performer.prompt, "<cyan>Add Performer</cyan>"),
        (add_writer.prompt, "<cyan>Add Writer</cyan>"),
        (add_to_collection.prompt, "<cyan>Add to Collection</cyan>"),
        (new_collection.prompt, "<cyan>New Collection</cyan>"),
        (update_watchlist_titles_table, "<cyan>Update IMDb data</cyan>"),
    ]

    option_function = radio_list.prompt(title="Manage Watchlist:", options=options,)

    if option_function:
        option_function()
        prompt()


def update_watchlist_titles_table() -> None:
    prompt_text = (
        "<cyan>This will update any non-frozen credits from the IMDb. Continue?</cyan>"
    )
    if confirm.prompt(prompt_text):
        watchlist.update_watchlist_titles_table()
