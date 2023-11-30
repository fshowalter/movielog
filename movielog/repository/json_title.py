from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from glob import glob
from pathlib import Path
from typing import Iterable, Optional, TypedDict, cast

import imdb
from slugify import slugify

from movielog import db
from movielog.moviedata import api as moviedata_api
from movielog.utils import format_tools, path_tools
from movielog.utils.logging import logger
from movielog.viewings import api as viewings_api
from movielog.watchlist import api as watchlist_api

imdb_http = imdb.IMDb(reraiseExceptions=True)
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

JsonPerformer = TypedDict(
    "JsonPerformer",
    {
        "imdbId": str,
        "name": str,
        "sequence": int,
        "roles": list[str],
    },
)

JsonDirector = TypedDict(
    "JsonDirector",
    {
        "imdbId": str,
        "name": str,
        "sequence": int,
    },
)

JsonTitle = TypedDict(
    "JsonTitle",
    {
        "slug": str,
        "imdbId": str,
        "title": str,
        "originalTitle": str,
        "sortTitle": str,
        "year": int,
        "releaseDate": str,
        "countries": list[str],
        "genres": list[str],
        "directors": list[JsonDirector],
        "performers": list[JsonPerformer],
        "writers": list[JsonWriter],
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


def create(
    imdb_id: str,
    title: str,
    year: int,
    release_date: str,
    countries: list[str],
    genres: list[str],
    directors: list[CreateTitleDirector],
    performers: list[CreateTitlePerformer],
    writers: list[CreateTitleWriter],
) -> JsonTitle:
    title_with_year = "{0} ({1})".format(title, year)
    slug = slugify(title_with_year, replacements=[("'", "")])

    json_title = JsonTitle(
        imdbId=imdb_id,
        title=title,
        originalTitle="",
        sortTitle=generate_sort_title(title=title, year=year),
        year=year,
        slug=slug,
        releaseDate=release_date,
        countries=countries,
        genres=genres,
        directors=[
            JsonDirector(
                imdbId=director.imdb_id,
                name=director.name,
                sequence=director.sequence,
            )
            for director in directors
        ],
        performers=[
            JsonPerformer(
                imdbId=performer.imdb_id,
                name=performer.name,
                sequence=performer.sequence,
                roles=performer.roles,
            )
            for performer in performers
        ],
        writers=[
            JsonWriter(
                imdbId=writer.imdb_id,
                name=writer.name,
                sequence=writer.sequence,
                notes=writer.notes,
            )
            for writer in writers
        ],
    )

    serialize(json_title)

    return json_title


@dataclass
class DbData(object):
    title: str
    year: int


def fetch_db_data(imdb_id: str) -> DbData:
    query = 'select title, year from movies where imdb_id="{0}"'

    row = db.fetch_all(query.format(imdb_id))[0]

    return DbData(title=row["title"], year=row["year"])


def parse_release_date(imdb_movie: imdb.Movie.Movie) -> str:
    re_match = re.search(r"(.*)\s\(", imdb_movie.get("original air date", ""))

    if not re_match:
        return "{0}-01-01".format(imdb_movie["year"])

    imdb_date = re_match.group(1)

    try:
        return (
            datetime.strptime(imdb_date, "%d %b %Y").date().isoformat()
        )  # noqa: WPS323
    except ValueError:
        try:  # noqa: WPS505
            return datetime.strptime(imdb_date, "%b %Y").date().isoformat()
        except ValueError:
            return "{0}-01-01".format(imdb_movie["year"])


def parse_roles(person: imdb.Person.Person) -> list[str]:
    if isinstance(person.currentRole, list):
        return [role["name"] for role in person.currentRole if role.keys()]

    if person.currentRole.has_key("name"):
        return [person.currentRole["name"]]

    return []


def build_performers(imdb_movie: imdb.Movie.Movie) -> list[JsonPerformer]:
    performers = []
    for index, performer in enumerate(imdb_movie["cast"]):
        if not moviedata_api.valid_cast_notes(performer):
            continue

        roles = parse_roles(performer)

        performers.append(
            JsonPerformer(
                imdbId="nm{0}".format(performer.personID),
                name=performer["name"],
                sequence=index,
                roles=roles,
            )
        )

    return performers


def reset() -> None:
    json_files = glob(os.path.join(FOLDER_NAME, "*.json"))
    total_count = len(json_files)

    for index, file_path in enumerate(json_files):
        with open(file_path, "r+") as json_file:
            json_title = cast(JsonTitle, json.load(json_file))

            updated_title = JsonTitle(
                imdbId=json_title["imdbId"],
                slug=json_title["slug"],
                title=json_title["title"],
                originalTitle=json_title["originalTitle"],
                sortTitle="{0} ({1})".format(
                    json_title["sortTitle"], json_title["year"]
                ),
                year=json_title["year"],
                releaseDate=json_title["releaseDate"],
                countries=json_title["countries"],
                genres=json_title["genres"],
                directors=json_title["directors"],
                performers=json_title["performers"],
                writers=json_title["writers"],
            )

            if updated_title == json_title:
                logger.log(
                    "{}/{} No updates for {}.",
                    index + 1,
                    total_count,
                    file_path,
                )
                continue

            json_file.seek(0)
            json_file.write(json.dumps(updated_title, default=str, indent=2))
            json_file.truncate()

            logger.log(
                "{}/{} Updated {}.",
                index + 1,
                total_count,
                file_path,
            )


def fix_all() -> None:
    processed_files = []
    existing_progress = []

    progress_file_path = os.path.join(FOLDER_NAME, ".progress")
    path_tools.ensure_file_path(progress_file_path)

    if os.path.isfile(progress_file_path):
        with open(progress_file_path, "r") as existing_progress_output_file:
            existing_progress = existing_progress_output_file.read().splitlines()

    try:
        json_files = glob(os.path.join(FOLDER_NAME, "*.json"))
        total_count = len(json_files)

        for index, file_path in enumerate(json_files):
            with open(file_path, "r+") as json_file:
                if file_path in existing_progress:
                    logger.log(
                        "{}/{} Skipped {} (already processed).",
                        index + 1,
                        total_count,
                        file_path,
                    )
                    continue

                json_title = cast(JsonTitle, json.load(json_file))
                imdb_movie = imdb_http.get_movie(json_title["imdbId"][2:])

                updated_title = JsonTitle(
                    imdbId=json_title["imdbId"],
                    slug=slugify(
                        "{0} ({1})".format(imdb_movie["title"], imdb_movie["year"]),
                        replacements=[("'", "")],
                    ),
                    title=imdb_movie["title"],
                    originalTitle=imdb_movie["original title"],
                    sortTitle=imdb_movie["canonical title"],
                    year=imdb_movie["year"],
                    releaseDate=parse_release_date(imdb_movie),
                    countries=imdb_movie["countries"],
                    genres=imdb_movie["genres"],
                    directors=[
                        JsonDirector(
                            imdbId="nm{0}".format(director.personID),
                            name=director["name"],
                            sequence=index,
                        )
                        for index, director in enumerate(imdb_movie["directors"])
                        if moviedata_api.valid_director_notes(director)
                    ],
                    performers=build_performers(imdb_movie),
                    writers=[
                        JsonWriter(
                            imdbId="nm{0}".format(writer.personID),
                            name=writer["name"],
                            sequence=index,
                            notes=None if writer.notes == "" else writer.notes,
                        )
                        for index, writer in enumerate(imdb_movie.get("writers", []))
                        if writer.keys() and moviedata_api.valid_writer_notes(writer)
                    ],
                )

                if updated_title == json_title:
                    logger.log(
                        "{}/{} No updates for {}.",
                        index + 1,
                        total_count,
                        file_path,
                    )
                    processed_files.append(file_path)
                    continue

                json_file.seek(0)
                json_file.write(json.dumps(updated_title, default=str, indent=2))
                json_file.truncate()

                logger.log(
                    "{}/{} Updated {}.",
                    index + 1,
                    total_count,
                    file_path,
                )

            processed_files.append(file_path)

    except:
        with open(progress_file_path, "a") as progress_output_file:
            progress_output_file.writelines(
                filename + "\n" for filename in processed_files
            )

        logger.log(
            "Wrote {}.",
            progress_file_path,
        )
        return

    if os.path.isfile(progress_file_path):
        os.unlink(progress_file_path)


def validate() -> None:
    viewing_movie_ids = viewings_api.movie_ids()
    watchlist_movie_ids = watchlist_api.movie_ids()

    valid_title_ids = viewing_movie_ids.union(watchlist_movie_ids)
    files_to_remove = []
    files_to_rename = []

    for file_path in glob(os.path.join(FOLDER_NAME, "*.json")):
        edited = False
        with open(file_path, "r+") as json_file:
            json_title = cast(JsonTitle, json.load(json_file))

            if json_title["imdbId"] not in valid_title_ids:
                logger.log(
                    "{0} not found. {1} marked for removal.",
                    json_title["imdbId"],
                    file_path,
                )
                files_to_remove.append(file_path)
                continue

            correct_slug = slugify(
                "{0} ({1})".format(json_title["title"], json_title["year"]),
                replacements=[("'", "")],
            )
            if json_title["slug"] != correct_slug:
                json_title["slug"] = correct_slug
                edited = True
                logger.log(
                    "{0} slug is {1} corrected to {2}.",
                    file_path,
                    json_title["slug"],
                    correct_slug,
                )

            correct_file_path = os.path.join(
                FOLDER_NAME, "{0}.json".format(json_title["slug"])
            )
            if file_path != correct_file_path:
                files_to_rename.append((file_path, correct_file_path))
                logger.log(
                    "{0} filename should be {1}. Marked for rename.",
                    file_path,
                    correct_file_path,
                )

            if json_title["slug"] != correct_slug:
                json_title["slug"] = correct_slug
                edited = True
                logger.log(
                    "{0} slug is {1} corrected to {2}.",
                    file_path,
                    json_title["slug"],
                    correct_slug,
                )

            if edited:
                json_file.seek(0)
                json_file.write(json.dumps(json_title, default=str, indent=2))
                json_file.truncate()
                logger.log(
                    "Wrote {}.",
                    file_path,
                )

    for file_path_to_remove in files_to_remove:
        Path.unlink(Path(file_path_to_remove))
        logger.log(
            "{0} removed.",
            file_path_to_remove,
        )

    for old_file_path, new_file_path in files_to_rename:
        os.rename(old_file_path, new_file_path)
        logger.log("{0} renamed to {1}.", old_file_path, new_file_path)


def migrate() -> None:
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
                countries=json_data["countries"],
                genres=json_data["genres"],
                directors=[
                    CreateTitleDirector(
                        imdb_id=director["person_imdb_id"],
                        name=director["name"],
                        sequence=director["sequence"],
                        notes=None if director["notes"] == "" else director["notes"],
                    )
                    for director in json_data["directors"]
                ],
                performers=[
                    CreateTitlePerformer(
                        imdb_id=performer["person_imdb_id"],
                        name=performer["name"],
                        sequence=performer["sequence"],
                        roles=performer["roles"],
                        notes=None if performer["notes"] == "" else performer["notes"],
                    )
                    for performer in json_data["cast"]
                ],
                writers=[
                    CreateTitleWriter(
                        imdb_id=writer["person_imdb_id"],
                        name=writer["name"],
                        sequence=index,
                        notes=None if writer["notes"] == "" else writer["notes"],
                    )
                    for index, writer in enumerate(json_data["writers"])
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


def deserialize_all() -> list[JsonTitle]:
    logger.log("==== Begin deserializing {}...", "titles")
    titles: list[JsonTitle] = []

    for file_path in glob(os.path.join(FOLDER_NAME, "*.json")):
        with open(file_path, "r") as json_file:
            titles.append(cast(JsonTitle, json.load(json_file)))

    logger.log(
        "Deserialized {} files.",
        format_tools.humanize_int(len(titles)),
    )

    return titles
