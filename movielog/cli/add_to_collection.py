import html
from typing import List, Optional, Sequence, Tuple

from movielog import watchlist
from movielog.cli import radio_list, select_movie

Collection = watchlist.Collection
Option = Tuple[Optional[Collection], str]


def prompt() -> None:
    collection = radio_list.prompt(title="Add to Collection:", options=build_options())

    if not collection:
        return

    movie = select_movie.prompt(prompt_text=select_movie_prompt_text(collection))
    if movie:
        collection.add_title(imdb_id=movie.imdb_id, title=movie.title, year=movie.year)
        collection.save()
    prompt()


def build_options() -> Sequence[Option]:
    options: List[Option] = [(None, "Go back")]

    for collection in watchlist.all_collections():
        option = f"<cyan>{collection.name}</cyan>"
        options.append((collection, option))

    return options


def select_movie_prompt_text(collection: Collection) -> str:
    formatted_titles = []
    for title in collection.titles:
        escaped_title = html.escape(title.title)
        formatted_title = f"<cyan>\u00B7</cyan> {escaped_title} ({title.year}) \n"
        formatted_titles.append(formatted_title)

    return "<cyan>{0}</cyan> titles:\n{1}\nNew Title: ".format(
        len(formatted_titles), "".join(formatted_titles)
    )
