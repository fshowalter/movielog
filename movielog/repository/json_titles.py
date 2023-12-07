from __future__ import annotations

import json
import os
from dataclasses import dataclass
from glob import glob
from pathlib import Path
from typing import Iterable, Optional, TypedDict, cast

import imdb
from slugify import slugify

from movielog.repository import slugifier
from movielog.utils import path_tools
from movielog.utils.logging import logger

imdb_http = imdb.IMDb(reraiseExceptions=True)
FOLDER_NAME = os.path.join("data", "titles")


JsonWriter = TypedDict(
    "JsonWriter",
    {
        "imdbId": str,
        "name": str,
        "notes": Optional[str],
    },
)

JsonPerformer = TypedDict(
    "JsonPerformer",
    {
        "imdbId": str,
        "name": str,
        "roles": list[str],
    },
)

JsonDirector = TypedDict(
    "JsonDirector",
    {
        "imdbId": str,
        "name": str,
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
        "runtimeMinutes": int,
        "imdbRating": Optional[float],
        "imdbVotes": Optional[int],
        "year": str,
        "releaseDate": str,
        "countries": list[str],
        "genres": list[str],
        "directors": list[JsonDirector],
        "performers": list[JsonPerformer],
        "writers": list[JsonWriter],
    },
)


def generate_sort_title(title: str, year: str) -> str:
    title_with_year = "{0} ({1})".format(title, year)
    title_lower = title_with_year.lower()
    title_words = title_with_year.split(" ")
    lower_words = title_lower.split(" ")
    articles = set(["a", "an", "the"])

    if (len(title_words) > 1) and (lower_words[0] in articles):
        return "{0}".format(" ".join(title_words[1 : len(title_words)]))

    return title_with_year


def generate_title_slug(title: str, year: str) -> str:
    return "{0}-({1})".format(slugifier.slugify_title(title), year)


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


def generate_file_path(json_title: JsonTitle) -> str:
    if not json_title["slug"]:
        json_title["slug"] = generate_title_slug(
            json_title["title"], json_title["year"]
        )

    file_name = "{0}-{1}.json".format(json_title["slug"], json_title["imdbId"][2:])
    return os.path.join(FOLDER_NAME, file_name)


def serialize(json_title: JsonTitle) -> None:
    file_path = generate_file_path(json_title)
    path_tools.ensure_file_path(file_path)

    with open(file_path, "w") as output_file:
        output_file.write(json.dumps(json_title, default=str, indent=2))

    logger.log(
        "Wrote {}.",
        file_path,
    )


def read_all() -> Iterable[JsonTitle]:
    for file_path in glob(os.path.join(FOLDER_NAME, "*.json")):
        with open(file_path, "r") as json_file:
            yield (cast(JsonTitle, json.load(json_file)))
