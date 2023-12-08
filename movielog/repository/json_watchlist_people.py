import json
import re
from typing import Iterable, Literal, TypedDict, Union, cast, get_args

from slugify import slugify

from movielog.repository import watchlist_serializer
from movielog.repository.json_watchlist_titles import JsonExcludedTitle, JsonTitle

JsonWatchlistPerson = TypedDict(
    "JsonWatchlistPerson",
    {
        "name": str,
        "slug": str,
        "imdbId": Union[str, list[str]],
        "titles": list[JsonTitle],
        "excludedTitles": list[JsonExcludedTitle],
    },
)

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
        raise ValueError(
            'Person in "{0}" with slug "{1}" already exists.'.format(
                watchlist, new_person_slug
            )
        )

    json_watchlist_person = JsonWatchlistPerson(
        imdbId=imdb_id, name=name, slug=new_person_slug, titles=[], excludedTitles=[]
    )

    serialize(json_watchlist_person, watchlist)

    return json_watchlist_person


def read_all(kind: Kind) -> Iterable[JsonWatchlistPerson]:
    for json_file in watchlist_serializer.read_all(kind):
        yield (cast(JsonWatchlistPerson, json.load(json_file)))


def title_sort_key(title: Union[JsonTitle, JsonExcludedTitle]) -> str:
    year_sort_regex = r"\(\d*\)"

    year = re.search(year_sort_regex, title["title"])

    if year:
        return "{0}-{1}".format(year.group(0), title["imdbId"])

    return "(????)-{0}".format(title["imdbId"])


def serialize(
    watchlist_person: JsonWatchlistPerson,
    kind: Kind,
) -> str:
    watchlist_person["titles"] = sorted(watchlist_person["titles"], key=title_sort_key)
    watchlist_person["excludedTitles"] = sorted(
        watchlist_person["excludedTitles"], key=title_sort_key
    )

    return watchlist_serializer.serialize(watchlist_person, folder_name=kind)
