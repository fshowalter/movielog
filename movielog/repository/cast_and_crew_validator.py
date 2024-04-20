from __future__ import annotations

import json
import os
from copy import deepcopy
from glob import glob
from typing import cast

from movielog.repository import (
    json_cast_and_crew,
    json_watchlist_people,
    markdown_reviews,
)
from movielog.utils.logging import logger


def get_watchlist_people() -> list[json_watchlist_people.JsonWatchlistPerson]:
    name_slugs: set[str] = set()
    watchlist_people: list[json_watchlist_people.JsonWatchlistPerson] = []

    for kind in json_watchlist_people.KINDS:
        for json_watchlist_person in json_watchlist_people.read_all(kind):
            assert json_watchlist_person["slug"] not in name_slugs
            watchlist_people.append(json_watchlist_person)
            name_slugs.add(json_watchlist_person["slug"])

    return watchlist_people


def validate_slug(json_name: json_cast_and_crew.JsonCastAndCrewMember) -> None:
    correct_slug = json_cast_and_crew.generate_name_slug(json_name["name"])

    existing_slug = json_name["slug"]

    if existing_slug == correct_slug:
        return

    logger.log(
        "Name {} [{}]: slug is {} but should be {}. {}",
        json_name["name"],
        json_name["imdbId"],
        existing_slug,
        correct_slug,
        "REVIEW",
    )


def get_review_ids() -> set[str]:
    return set([review.yaml["imdb_id"] for review in markdown_reviews.read_all()])


def add_new_cast_and_crew(
    watchlist_people: list[json_watchlist_people.JsonWatchlistPerson],
) -> None:
    for index, watchlist_person in enumerate(watchlist_people):
        logger.log(
            "{}/{} adding {}...",
            index + 1,
            len(watchlist_people),
            watchlist_person["name"],
        )

        new_member = json_cast_and_crew.JsonCastAndCrewMember(
            imdbId=watchlist_person["imdbId"],
            name=watchlist_person["name"],
            slug=watchlist_person["slug"],
        )

        json_cast_and_crew.serialize(new_member)


def rename_files_marked_for_rename(
    files_marked_for_rename: list[tuple[str, str]]
) -> None:
    for old_file_path, new_file_path in files_marked_for_rename:
        os.rename(old_file_path, new_file_path)
        logger.log("{0} renamed to {1}.", old_file_path, new_file_path)


def validate() -> None:  # noqa: WPS210, WPS213
    watchlist_people = get_watchlist_people()
    files_to_rename = []

    for file_path in glob(os.path.join(json_cast_and_crew.FOLDER_NAME, "*.json")):
        with open(file_path, "r+") as json_file:
            json_name = cast(
                json_cast_and_crew.JsonCastAndCrewMember, json.load(json_file)
            )

            updated_name = deepcopy(json_name)

            validate_slug(updated_name)

            correct_file_path = json_cast_and_crew.generate_file_path(updated_name)

            if file_path != correct_file_path:
                files_to_rename.append((file_path, correct_file_path))
                logger.log(
                    "{} filename should be {}. {}",
                    file_path,
                    correct_file_path,
                    "Marked for rename.",
                )

            watchlist_people = [
                watchlist_person
                for watchlist_person in watchlist_people
                if watchlist_person["imdbId"] != json_name["imdbId"]
            ]

    rename_files_marked_for_rename(files_to_rename)

    add_new_cast_and_crew(watchlist_people)
