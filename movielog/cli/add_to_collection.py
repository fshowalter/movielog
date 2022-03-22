from __future__ import annotations

import html
from typing import Optional, Sequence, Tuple

from movielog import api as movielog_api
from movielog.cli import radio_list, select_movie

Collection = movielog_api.Collection
Option = Tuple[Optional[Collection], str]


def prompt() -> None:
    collection = radio_list.prompt(title="Add to Collection:", options=build_options())

    if not collection:
        return

    movie = select_movie.prompt(prompt_text=select_movie_prompt_text(collection))
    if movie:
        movielog_api.add_movie_to_collection(
            collection=collection,
            imdb_id=movie.imdb_id,
            title=movie.title,
            year=movie.year,
        )
    prompt()


def build_options() -> Sequence[Option]:
    options: list[Option] = [(None, "Go back")]

    for collection in movielog_api.collections():
        option = "<cyan>{0}</cyan>".format(collection.name)
        options.append((collection, option))

    return options


def select_movie_prompt_text(collection: Collection) -> str:
    formatted_titles = []
    for movie in collection.movies:
        escaped_title = html.escape(movie.title)
        formatted_title = "<cyan>\u00B7</cyan> {0} ({1}) \n".format(
            escaped_title, movie.year
        )
        formatted_titles.append(formatted_title)

    return "<cyan>{0}</cyan> titles:\n{1}\nNew Title: ".format(
        len(formatted_titles), "".join(formatted_titles)
    )
