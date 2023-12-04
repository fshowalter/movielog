from __future__ import annotations

import os
import re
from collections.abc import Generator
from contextlib import contextmanager
from typing import Optional, Union

from movielog.repository import (
    credit_notes_validator,
    imdb_http,
    json_watchlist_people,
    watchlist_serializer,
)
from movielog.repository.json_watchlist_titles import JsonExcludedTitle, JsonTitle
from movielog.utils import path_tools
from movielog.utils.logging import logger

VALID_KINDS = (
    "movie",
    "tv movie",
    "video movie",
)


def add_to_person_excluded_titles(
    imdb_movie: imdb_http.Movie,
    person: json_watchlist_people.JsonWatchlistPerson,
    reason: str,
) -> None:
    excluded_title = JsonExcludedTitle(
        imdbId=imdb_movie.imdb_id, title=imdb_movie.full_title, reason=reason
    )

    person["excludedTitles"].append(excluded_title)

    logger.log(
        "{} added to {} ({}).",
        excluded_title["title"],
        "excludedTitles",
        excluded_title["reason"],
    )


def title_sort_key(title: Union[JsonTitle, JsonExcludedTitle]) -> str:
    year_sort_regex = r"\(\d*\)"

    year = re.search(year_sort_regex, title["title"])

    if year:
        return "{0}-{1}".format(year.group(0), title["imdbId"])

    return "(????)-{0}".format(title["imdbId"])


def invalid_credit_notes(
    imdb_movie: imdb_http.Movie,
    person: json_watchlist_people.JsonWatchlistPerson,
    kind: imdb_http.CreditKind,
) -> Optional[str]:
    credits_for_person = [credit for credit in imdb_movie.credits[kind]]

    valid_credits = []
    invalid_credits = []

    for credit in credits_for_person:
        valid, notes = credit_notes_validator.credit_notes_are_valid_for_kind(
            credit.notes, kind
        )
        if valid:
            valid_credits.append(credit)
        else:
            invalid_credits.append(credit)

    if valid_credits:
        return None

    return " / ".join(
        [
            invalid_credit.notes
            for invalid_credit in invalid_credits
            if invalid_credit.notes
        ]
    )


def parse_credit_title_ids_for_person(
    person: json_watchlist_people.JsonWatchlistPerson, kind: imdb_http.CreditKind
) -> set[str]:
    if isinstance(person["imdbId"], str):
        imdb_person = imdb_http.get_person(person["imdbId"])
        return set([credit.imdb_id for credit in imdb_person.credits[kind]])

    filmographies: list[set[str]] = []
    for imdb_id in person["imdbId"]:
        imdb_person = imdb_http.get_person(imdb_id)
        filmographies.append(
            set(credit.imdb_id for credit in imdb_person.credits[kind])
        )

    return set.intersection(*filmographies)


def remove_missing_titles(
    person: json_watchlist_people.JsonWatchlistPerson, credit_title_ids: set[str]
) -> None:
    existing_title_ids = set([title["imdbId"] for title in person["titles"]])

    missing_titles = (
        title
        for title in person["titles"]
        if title["imdbId"] in existing_title_ids - credit_title_ids
    )

    for missing_title in missing_titles:
        person["titles"].remove(missing_title)
        logger.log(
            "Missing title {} removed.",
            missing_title["title"],
        )

    existing_excluded_title_ids = set(
        [title["imdbId"] for title in person["excludedTitles"]]
    )

    missing_excluded_titles = (
        title
        for title in person["excludedTitles"]
        if title["imdbId"] in existing_excluded_title_ids - credit_title_ids
    )

    for missing_exluded_title in missing_excluded_titles:
        person["excludedTitles"].remove(missing_exluded_title)
        logger.log(
            "Missing excluded title {} removed.",
            missing_exluded_title["title"],
        )


def skip_existing_titles(
    person: json_watchlist_people.JsonWatchlistPerson, credit_title_ids: set[str]
) -> set[str]:
    existing_excluded_title_ids = [
        excluded_title["imdbId"] for excluded_title in person["excludedTitles"]
    ]

    existing_title_ids = [title["imdbId"] for title in person["titles"]]

    return credit_title_ids.difference(existing_excluded_title_ids).difference(
        existing_title_ids
    )


def update_entity_titles(
    person: json_watchlist_people.JsonWatchlistPerson, kind: imdb_http.CreditKind
) -> None:
    credit_title_ids = parse_credit_title_ids_for_person(person=person, kind=kind)

    remove_missing_titles(person=person, credit_title_ids=credit_title_ids)

    new_credit_title_ids = skip_existing_titles(
        person=person, credit_title_ids=credit_title_ids
    )

    for index, imdb_id in enumerate(new_credit_title_ids):
        logger.log(
            "{}/{} fetching data for {}...",
            index + 1,
            len(new_credit_title_ids),
            imdb_id,
        )

        imdb_movie = imdb_http.get_movie(imdb_id)

        if imdb_movie.production_status:
            logger.log(
                "Skipping {} for {} production status: {}",
                imdb_movie.full_title,
                person["name"],
                imdb_movie.production_status,
            )
            continue

        if imdb_movie.kind not in VALID_KINDS:
            add_to_person_excluded_titles(
                imdb_movie=imdb_movie, person=person, reason=imdb_movie.kind
            )
            continue

        invalid_genres = {"Adult", "Short", "Documentary"} & imdb_movie.genres
        if invalid_genres:
            add_to_person_excluded_titles(
                imdb_movie=imdb_movie,
                person=person,
                reason="{0}".format(", ".join(invalid_genres)),
            )
            continue

        if "Silent" in imdb_movie.sound_mix:
            add_to_person_excluded_titles(
                imdb_movie=imdb_movie,
                person=person,
                reason="silent",
            )
            continue

        invalid_notes = invalid_credit_notes(
            imdb_movie=imdb_movie, person=person, kind=kind
        )
        if invalid_notes:
            add_to_person_excluded_titles(
                imdb_movie=imdb_movie,
                person=person,
                reason=invalid_notes,
            )
            continue

        person["titles"].append(
            JsonTitle(
                imdbId=imdb_movie.imdb_id,
                title=imdb_movie.full_title,
            )
        )

        logger.log(
            "{} added to {}.",
            imdb_movie.full_title,
            "titles",
        )

    person["titles"] = sorted(person["titles"], key=title_sort_key)

    person["excludedTitles"] = sorted(person["excludedTitles"], key=title_sort_key)


@contextmanager
def checkpoint(kind: json_watchlist_people.Kind) -> Generator[list[str]]:
    progress = []

    progress_file_path = os.path.join(
        watchlist_serializer.FOLDER_PATH, kind, ".progress"
    )
    path_tools.ensure_file_path(progress_file_path)

    if os.path.isfile(progress_file_path):
        with open(progress_file_path, "r") as existing_progress_output_file:
            progress = existing_progress_output_file.read().splitlines()

    try:
        yield progress
    finally:
        with open(progress_file_path, "w") as progress_output_file:
            progress_output_file.writelines(filename + "\n" for filename in progress)

        logger.log(
            "Wrote {}.",
            progress_file_path,
        )


WatchlistKindToCreditKind: dict[json_watchlist_people.Kind, imdb_http.CreditKind] = {
    "directors": "director",
    "performers": "performer",
    "writers": "writer",
}


def update_watchlist_credits() -> None:
    for kind in json_watchlist_people.KINDS:
        watchlist_people = list(json_watchlist_people.read_all(kind))
        with checkpoint(kind=kind) as processed_files:
            for index, watchlist_entity in enumerate(watchlist_people):
                logger.log(
                    "==== Begin getting {} credits for {}...",
                    kind,
                    watchlist_entity["name"],
                )

                if watchlist_entity["slug"] in processed_files:
                    logger.log(
                        "{}/{} Skipped {} (already processed).",
                        index + 1,
                        len(watchlist_people),
                        watchlist_entity["name"],
                    )
                    continue

                update_entity_titles(watchlist_entity, WatchlistKindToCreditKind[kind])

                watchlist_serializer.serialize(watchlist_entity, kind)

                processed_files.append(watchlist_entity["slug"])
