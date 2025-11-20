from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import cast

from movielog.repository import json_cast_and_crew, json_watchlist_people
from movielog.repository.json_watchlist_person import JsonWatchlistPerson
from movielog.utils.logging import logger


def _get_watchlist_people() -> list[JsonWatchlistPerson]:
    name_slugs: set[str] = set()
    watchlist_people: list[JsonWatchlistPerson] = []

    for kind in json_watchlist_people.KINDS:
        for json_watchlist_person in json_watchlist_people.read_all(kind):
            assert json_watchlist_person["slug"] not in name_slugs
            watchlist_people.append(json_watchlist_person)
            name_slugs.add(json_watchlist_person["slug"])

    return watchlist_people


def _validate_slug(json_name: json_cast_and_crew.JsonCastAndCrewMember) -> None:
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


def _add_new_cast_and_crew(
    watchlist_people: list[JsonWatchlistPerson],
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


def _rename_files_marked_for_rename(files_marked_for_rename: list[tuple[Path, Path]]) -> None:
    for old_file_path, new_file_path in files_marked_for_rename:
        Path.rename(old_file_path, new_file_path)
        logger.log("{0} renamed to {1}.", old_file_path, new_file_path)


def validate() -> None:
    watchlist_people = _get_watchlist_people()
    files_to_rename = []

    for file_path in Path(json_cast_and_crew.FOLDER_NAME).glob("*.json"):
        with Path.open(file_path, "r+") as json_file:
            json_name = cast(json_cast_and_crew.JsonCastAndCrewMember, json.load(json_file))

            updated_name = deepcopy(json_name)

            _validate_slug(updated_name)

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

    _rename_files_marked_for_rename(files_to_rename)

    _add_new_cast_and_crew(watchlist_people)
