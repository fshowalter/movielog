import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Literal, cast, get_args

from slugify import slugify

from movielog.repository import watchlist_serializer
from movielog.repository.json_watchlist_person import JsonWatchlistPerson
from movielog.repository.json_watchlist_titles import JsonExcludedTitle, JsonWatchlistTitle

Kind = Literal[
    "directors",
    "writers",
    "performers",
]

KINDS = get_args(Kind)


def create(watchlist: Kind, imdb_id: str, name: str) -> JsonWatchlistPerson:
    new_person_slug = slugify(name)

    existing_person = next(
        (person for person in read_all(watchlist) if person["slug"] == new_person_slug),
        None,
    )

    if existing_person:
        raise ValueError(f'Person in "{watchlist}" with slug "{new_person_slug}" already exists.')

    json_watchlist_person = JsonWatchlistPerson(
        imdbId=imdb_id, name=name, slug=new_person_slug, titles=[], excludedTitles=[]
    )

    serialize(json_watchlist_person, watchlist)

    return json_watchlist_person


def read_all(kind: Kind) -> Iterable[JsonWatchlistPerson]:
    for json_file in watchlist_serializer.read_all(kind):
        yield (cast(JsonWatchlistPerson, json.load(json_file)))


def title_sort_key(title: JsonWatchlistTitle | JsonExcludedTitle) -> str:
    year_sort_regex = r"\(\d*\)"

    year = re.search(year_sort_regex, title["title"])

    if year:
        return "{}-{}".format(year.group(0), title["imdbId"])

    return "(????)-{}".format(title["imdbId"])


def serialize(
    watchlist_person: JsonWatchlistPerson,
    kind: Kind,
) -> Path:
    watchlist_person["titles"] = sorted(watchlist_person["titles"], key=title_sort_key)
    watchlist_person["excludedTitles"] = sorted(
        watchlist_person["excludedTitles"], key=title_sort_key
    )

    return watchlist_serializer.serialize(watchlist_person, folder_name=kind)
