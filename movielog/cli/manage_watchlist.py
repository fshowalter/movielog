from movielog.cli import (
    add_director,
    add_performer,
    add_to_collection,
    add_writer,
    new_collection,
    radio_list,
)


def prompt() -> None:
    options = [
        (add_director.prompt, "<cyan>Add Director</cyan>"),
        (add_performer.prompt, "<cyan>Add Performer</cyan>"),
        (add_writer.prompt, "<cyan>Add Writer</cyan>"),
        (add_to_collection.prompt, "<cyan>Add to Collection</cyan>"),
        (new_collection.prompt, "<cyan>New Collection</cyan>"),
    ]

    option_function = radio_list.prompt(
        title="Manage Watchlist:",
        options=options,
    )

    if option_function:
        option_function()
        prompt()
