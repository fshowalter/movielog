from __future__ import annotations

import json
import os
from collections import defaultdict
from dataclasses import dataclass
from glob import glob
from typing import Iterable, Optional, TypedDict, cast

from slugify import slugify

from movielog import db
from movielog.utils import path_tools
from movielog.utils.logging import logger

FOLDER_NAME = "titles"


JsonWriter = TypedDict(
    "JsonWriter",
    {
        "imdbId": str,
        "name": str,
        "sequence": int,
        "notes": Optional[str],
    },
)

JsonWriterGroup = TypedDict(
    "JsonWriterGroup",
    {
        "sequence": int,
        "writers": list[JsonWriter],
    },
)

JsonPerformer = TypedDict(
    "JsonPerformer",
    {
        "imdbId": str,
        "name": str,
        "sequence": int,
        "roles": list[str],
        "notes": Optional[str],
    },
)

JsonDirector = TypedDict(
    "JsonDirector",
    {
        "imdbId": str,
        "name": str,
        "sequence": int,
        "notes": Optional[str],
    },
)

JsonTitle = TypedDict(
    "JsonTitle",
    {
        "slug": str,
        "imdbId": str,
        "title": str,
        "sortTitle": str,
        "year": int,
        "releaseDate": str,
        "releaseDateNotes": Optional[str],
        "countries": list[str],
        "genres": list[str],
        "directors": list[JsonDirector],
        "performers": list[JsonPerformer],
        "writers": list[JsonWriterGroup],
    },
)


def generate_sort_title(title: str, year: int) -> str:
    title_with_year = "{0} ({1})".format(title, year)
    title_lower = title_with_year.lower()
    title_words = title_with_year.split(" ")
    lower_words = title_lower.split(" ")
    articles = set(["a", "an", "the"])

    if (len(title_words) > 1) and (lower_words[0] in articles):
        return "{0}".format(" ".join(title_words[1 : len(title_words)]))

    return title_with_year


@dataclass
class CreateTitleDirector(object):
    imdb_id: str
    name: str
    sequence: int
    notes: Optional[str]


@dataclass
class CreateTitlePerformer(object):
    imdb_id: str
    name: str
    sequence: int
    roles: list[str]
    notes: Optional[str]


@dataclass
class CreateTitleWriter(object):
    imdb_id: str
    name: str
    sequence: int
    notes: Optional[str]


@dataclass
class CreateTitleWriterGroup(object):
    sequence: int
    writers: list[CreateTitleWriter]


def create(
    imdb_id: str,
    title: str,
    year: int,
    release_date: str,
    release_date_notes: Optional[str],
    countries: list[str],
    genres: list[str],
    directors: list[CreateTitleDirector],
    performers: list[CreateTitlePerformer],
    writers: list[CreateTitleWriterGroup],
) -> JsonTitle:
    title_with_year = "{0} ({1})".format(title, year)
    slug = slugify(title_with_year, replacements=[("'", "")])

    json_title = JsonTitle(
        imdbId=imdb_id,
        title=title,
        sortTitle=generate_sort_title(title=title, year=year),
        year=year,
        slug=slug,
        releaseDate=release_date,
        releaseDateNotes=release_date_notes,
        countries=countries,
        genres=genres,
        directors=[
            JsonDirector(
                imdbId=director.imdb_id,
                name=director.name,
                sequence=director.sequence,
                notes=director.notes,
            )
            for director in directors
        ],
        performers=[
            JsonPerformer(
                imdbId=performer.imdb_id,
                name=performer.name,
                sequence=performer.sequence,
                roles=performer.roles,
                notes=performer.notes,
            )
            for performer in performers
        ],
        writers=[
            JsonWriterGroup(
                sequence=group.sequence,
                writers=[
                    JsonWriter(
                        imdbId=writer.imdb_id,
                        name=writer.name,
                        sequence=writer.sequence,
                        notes=writer.notes,
                    )
                    for writer in group.writers
                ],
            )
            for group in writers
        ],
    )

    serialize(json_title)

    return json_title


@dataclass
class DbData(object):
    title: str
    year: int


def fetch_db_data(imdb_id: str) -> DbData:
    query = "select title, year from movies where imdb_id={0}"

    row = db.fetch_all(query.format(imdb_id))[0]

    return DbData(title=row["title"], year=row["year"])


def fix_all() -> None:
    for file_path in glob(os.path.join("data", "*.json")):
        with open(file_path, "r") as json_file:
            json_data = json.load(json_file)
            db_data = fetch_db_data(json_data["imdb_id"])

            writers_by_group = defaultdict(list)

            for writer in json_data["writers"]:
                writers_by_group[writer["group"]].append(writer)

            create(
                imdb_id=json_data["imdb_id"],
                title=db_data.title,
                year=db_data.year,
                release_date=json_data["release_date"],
                release_date_notes=json_data["release_date_notes"],
                countries=json_data["countries"],
                genres=json_data["genres"],
                directors=[
                    CreateTitleDirector(
                        imdb_id=director["person_imdb_id"],
                        name=director["name"],
                        sequence=director["sequence"],
                        notes=director["notes"],
                    )
                    for director in json_data["directors"]
                ],
                performers=[
                    CreateTitlePerformer(
                        imdb_id=performer["person_imdb_id"],
                        name=performer["name"],
                        sequence=performer["sequence"],
                        roles=performer["roles"],
                        notes=performer["notes"],
                    )
                    for performer in json_data["cast"]
                ],
                writers=[
                    CreateTitleWriterGroup(
                        sequence=group,
                        writers=[
                            CreateTitleWriter(
                                imdb_id=writer["person_imdb_id"],
                                name=writer["name"],
                                sequence=writer["sequence"],
                                notes=writer["notes"],
                            )
                            for writer in writers
                        ],
                    )
                    for group, writers in writers_by_group.items()
                ],
            )


def serialize(json_title: JsonTitle) -> None:
    file_path = os.path.join(FOLDER_NAME, "{0}.json".format(json_title["slug"]))
    path_tools.ensure_file_path(file_path)

    with open(file_path, "w") as output_file:
        output_file.write(json.dumps(json_title, default=str, indent=2))

    logger.log(
        "Wrote {}.",
        file_path,
    )
