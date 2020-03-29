from prompt_toolkit.formatted_text import HTML

from movie_db.cli import (
    _radio_list,
    add_director,
    add_performer,
    add_to_collection,
    add_writer,
    new_collection,
)


def prompt() -> None:
    options = _radio_list.CallableOptions([
        (None, 'Go back'),
        (
            add_director.prompt,
            HTML('<cyan>Add Director</cyan>'),
        ),
        (
            add_performer.prompt,
            HTML('<cyan>Add Performer</cyan>'),
        ),
        (
            add_writer.prompt,
            HTML('<cyan>Add Writer</cyan>'),
        ),
        (
            add_to_collection.prompt,
            HTML('<cyan>Add to Collection</cyan>'),
        ),
        (
            new_collection.prompt,
            HTML('<cyan>New Collection</cyan>'),
        ),
    ])

    option_function = _radio_list.prompt(
        title='Manage Watchlist:',
        options=options,
    )

    if option_function:
        option_function()
        prompt()
