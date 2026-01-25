from __future__ import annotations

import html
from collections.abc import Sequence

from movielog.cli import radio_list, select_title
from movielog.repository import api as repository_api

Collection = repository_api.Collection
Option = tuple[Collection | None, str]


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
        (collection, f"<cyan>{collection.name}</cyan>")
        for collection in repository_api.collections()
    ]


def select_movie_prompt_text(collection: Collection) -> str:
    formatted_titles = []

    for title in repository_api.titles():
        if title.imdb_id not in collection.title_ids:
            continue

        escaped_title = html.escape(title.title)
        formatted_title = f"<cyan>\u00b7</cyan> {escaped_title} ({title.release_year}) \n"
        formatted_titles.append(formatted_title)

    return "<cyan>{}</cyan> titles:\n{}\nNew Title: ".format(
        len(formatted_titles), "".join(formatted_titles)
    )
