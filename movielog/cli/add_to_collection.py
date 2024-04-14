from __future__ import annotations

import html
from typing import Optional, Sequence, Tuple

from movielog.cli import radio_list, select_title
from movielog.repository import api as repository_api

Collection = repository_api.Collection
Option = Tuple[Optional[Collection], str]


def prompt() -> None:
    collection = radio_list.prompt(title="Add to Collection:", options=build_options())

    if not collection:
        return

    title = select_title.prompt(prompt_text=select_movie_prompt_text(collection))
    if title:
        repository_api.add_title_to_collection(
            collection=collection,
            imdb_id=title.imdb_id,
            full_title=title.full_title,
        )
    prompt()


def build_options() -> Sequence[Option]:
    return [
        (collection, "<cyan>{0}</cyan>".format(collection.name))
        for collection in repository_api.collections()
    ]


def select_movie_prompt_text(collection: Collection) -> str:
    formatted_titles = []

    for title in repository_api.titles():
        if title.imdb_id not in collection.title_ids:
            continue

        escaped_title = html.escape(title.title)
        formatted_title = "<cyan>\u00B7</cyan> {0} ({1}) \n".format(
            escaped_title, title.year
        )
        formatted_titles.append(formatted_title)

    return "<cyan>{0}</cyan> titles:\n{1}\nNew Title: ".format(
        len(formatted_titles), "".join(formatted_titles)
    )
