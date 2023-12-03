from __future__ import annotations

import os
import re
from collections.abc import Generator
from contextlib import contextmanager
from typing import Callable, Optional, Union

from movielog.moviedata import api as moviedata_api
from movielog.repository import imdb_http, json_watchlist_people, watchlist_serializer
from movielog.repository.json_watchlist_titles import JsonExcludedTitle, JsonTitle
from movielog.utils import path_tools
from movielog.utils.logging import logger

VALID_KINDS = (
    "movie",
    "tv movie",
    "video movie",
)


def log_excluded_title(
    index: int, total: int, excluded_title: JsonExcludedTitle
) -> None:
    logger.log(
        "{}/{} {} added to {} ({}).",
        index,
        total,
        excluded_title["title"],
        "excludedTitles",
        excluded_title["reason"],
    )


def add_to_person_excluded_titles(
    imdb_movie: imdb_http.Movie,
    person: json_watchlist_people.JsonWatchlistPerson,
    reason: str,
) -> JsonExcludedTitle:
    excluded_title = JsonExcludedTitle(
        imdbId=imdb_movie.imdb_id, title=imdb_movie.full_title, reason=reason
    )

    person["excludedTitles"].append(excluded_title)

    return excluded_title


def title_sort_key(title: Union[JsonTitle, JsonExcludedTitle]) -> str:
    year_sort_regex = r"\(\d*\)"

    year = re.search(year_sort_regex, title["title"])

    if year:
        return "{0}-{1}".format(year.group(0), title["imdbId"])

    return "(????)-{0}".format(title["imdbId"])


def valid_for_director(
    imdb_movie: imdb_http.Movie, person: json_watchlist_people.JsonWatchlistPerson
) -> Optional[str]:
    len(imdb_movie.credits_for_person(person["imdbId"])) == len(
        imdb_movie.invalid_credits_for_person(person["imdbId"])
    )

    invalid_credit_notes = [
        credit.notes
        for credit in credits
        if credit.notes
        and ("scenes deleted" in credit.notes or "uncredited" in credit.notes)
    ]

    if len(credits) - len(invalid_credit_notes) == 0:
        return " / ".join(invalid_credit_notes)

    return None


def valid_for_performe(
    imdb_movie: imdb_http.Movie, person: json_watchlist_people.JsonWatchlistPerson
) -> Optional[str]:
    performer_notes = set(
        [
            credit.notes
            for credit in imdb_movie.get("cast", [])
            if "nm{0}".format(credit.personID) in person.imdbId
        ]
    )

    imdb_movie.notes = " / ".join(performer_notes)

    if not moviedata_api.valid_cast_notes(imdb_movie):
        return imdb_movie.notes

    return None


def valid_for_writer(
    imdb_movie: imdb_http.Movie, person: json_watchlist_people.JsonWatchlistPerson
) -> Optional[str]:
    writer_notes = set(
        [
            credit.notes
            for credit in imdb_movie.get("writers", [])
            if "nm{0}".format(credit.personID) in person.imdbId
        ]
    )

    imdb_movie.notes = " / ".join(writer_notes)

    if not moviedata_api.valid_writer_notes(imdb_movie):
        return imdb_movie.notes

    return None


NotesValidator: dict[imdb_http.CreditKind, Callable] = {
    "director": valid_for_director,
    "writer": valid_for_writer,
    "performer": valid_for_performer,
}


def parse_credit_title_ids_for_person(
    person: json_watchlist_people.JsonWatchlistPerson, kind: imdb_http.CreditKind
) -> set(str):
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
    missing_title_ids = existing_title_ids - credit_title_ids

    for index, missing_title_id in enumerate(missing_title_ids):
        missing_title = next(
            (
                title
                for title in person["titles"]
                if title["imdbId"] == missing_title_id
            ),
            None,
        )

        if missing_title:
            person["titles"].remove(missing_title)
            logger.log(
                "{}/{} missing title {} removed.",
                index + 1,
                len(missing_title_ids),
                missing_title_id,
            )


def remove_missing_excluded_titles(
    person: json_watchlist_people.JsonWatchlistPerson, credit_title_ids: set[str]
) -> None:
    existing_excluded_title_ids = set(
        [title["imdbId"] for title in person["excludedTitles"]]
    )

    missing_excluded_title_ids = existing_excluded_title_ids - credit_title_ids

    for index, missing_excluded_title_id in enumerate(missing_excluded_title_ids):
        missing_excluded_title = next(
            (
                excluded_title
                for excluded_title in person["excludedTitles"]
                if excluded_title["imdbId"] == missing_excluded_title_id
            ),
            None,
        )

        if missing_excluded_title:
            person["excludedTitles"].remove(missing_excluded_title)
            logger.log(
                "{}/{} missing excluded title {} removed.",
                index + 1,
                len(missing_excluded_title_ids),
                missing_excluded_title_id,
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

    remove_missing_excluded_titles(person=person, credit_title_ids=credit_title_ids)

    new_credit_title_ids = skip_existing_titles(
        person=person, credit_title_ids=credit_title_ids
    )

    for index, imdb_id in enumerate(new_credit_title_ids):
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
            excluded_title = add_to_person_excluded_titles(
                imdb_movie=imdb_movie, person=person, reason=imdb_movie.kind
            )
            log_excluded_title(
                index=index,
                total=len(new_credit_title_ids),
                excluded_title=excluded_title,
            )
            continue

        invalid_genres = {"Adult", "Short", "Documentary"} & imdb_movie.genres
        if invalid_genres:
            excluded_title = add_to_person_excluded_titles(
                imdb_movie=imdb_movie,
                person=person,
                reason="{0}".format(", ".join(invalid_genres)),
            )
            log_excluded_title(
                index=index,
                total=len(new_credit_title_ids),
                excluded_title=excluded_title,
            )
            continue

        if "Silent" in imdb_movie.sound_mix:
            excluded_title = add_to_person_excluded_titles(
                imdb_movie=imdb_movie,
                person=person,
                reason="silent",
            )
            log_excluded_title(
                index=index,
                total=len(new_credit_title_ids),
                excluded_title=excluded_title,
            )
            continue

        # invalid_notes = validator(imdb_movie, person)
        # if invalid_notes:
        #     person.excludedTitles.append(
        #         JsonExcludedTitle(
        #             imdbId="tt{0}".format(imdb_movie.movieID),
        #             title=imdb_movie["long imdb title"],
        #             reason=invalid_notes,
        #         )
        #     )
        #     logger.log(
        #         "{}/{} {} added to {} ({}).",
        #         index + 1,
        #         total_filmography,
        #         imdb_movie["long imdb title"],
        #         "excludedTitles",
        #         invalid_notes,
        #     )
        #     continue

        person["titles"].append(
            JsonTitle(
                imdbId=imdb_movie.imdb_id,
                title=imdb_movie.full_title,
            )
        )
        logger.log(
            "{}/{} {} added to {}.",
            index + 1,
            len(new_credit_title_ids),
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
