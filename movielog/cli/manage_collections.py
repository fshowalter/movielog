from movielog.cli import add_to_collection, new_collection, radio_list


def prompt() -> None:
    options = [
        (add_to_collection.prompt, "<cyan>Add to existing Collection</cyan>"),
        (new_collection.prompt, "<cyan>Create new Collection</cyan>"),
    ]

    option_function = radio_list.prompt(
        title="Manage Collections:",
        options=options,
    )

    if option_function:
        option_function()
        prompt()
