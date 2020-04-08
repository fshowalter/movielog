import html
from typing import List, Optional, Sequence, Tuple

from prompt_toolkit.formatted_text import HTML

from movielog import watchlist_collection
from movielog.cli import ask, queries, radio_list, select_movie

Option = Tuple[Optional[watchlist_collection.Collection], str]


def prompt() -> None:
    collection = radio_list.prompt(
        title=HTML("Add to Collection:"), options=_build_add_to_collection_options(),
    )

    if collection:
        movie = select_movie.prompt()
        if movie:
            collection.add_title(
                imdb_id=movie.imdb_id, title=movie.title, year=movie.year
            )
            collection.save()
        prompt()


def _build_add_to_collection_options() -> Sequence[Option]:
    options: List[Option] = [(None, "Go back")]

    for collection in watchlist_collection.all_items():
        option = HTML(f"<cyan>{collection.name}</cyan>")
        options.append((collection, option))

    return options


def _prompt_for_new_title(collection: watchlist_collection.Collection) -> Optional[str]:
    formatted_titles = []
    for title in collection.titles:
        escaped_title = html.escape(title.title)
        formatted_title = f"\u00B7 {escaped_title} ({title.year}) \n"
        formatted_titles.append(formatted_title)

    prompt_text = HTML(
        "<cyan>{0}</cyan> titles:\n{1}\nNew Title: ".format(
            len(formatted_titles), "".join(formatted_titles),
        ),
    )
    return ask.prompt(prompt_text)
