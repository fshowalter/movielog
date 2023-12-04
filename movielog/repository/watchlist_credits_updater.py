from __future__ import annotations

import os

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


def add_title_page_to_watchlist_person_excluded_titles(
    title_page: imdb_http.TitlePage,
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    reason: str,
) -> None:
    excluded_title = JsonExcludedTitle(
        imdbId=title_page.imdb_id, title=title_page.full_title, reason=reason
    )

    watchlist_person["excludedTitles"].append(excluded_title)

    logger.log(
        "{} added to {} ({}).",
        excluded_title["title"],
        "excludedTitles",
        excluded_title["reason"],
    )


def add_title_page_to_watchlist_person_titles(
    title_page: imdb_http.TitlePage,
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
) -> None:
    watchlist_person["titles"].append(
        JsonTitle(
            imdbId=title_page.imdb_id,
            title=title_page.full_title,
        )
    )

    logger.log(
        "{} added to {}.",
        title_page.full_title,
        "titles",
    )


def all_credits_on_title_page_are_invalid_for_watchlist_person(  # noqa: WPS210
    title_page: imdb_http.TitlePage,
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    kind: imdb_http.CreditKind,
) -> tuple[bool, str]:
    credits_for_person = [
        credit
        for credit in title_page.credits[kind]
        if credit.imdb_id == watchlist_person["imdbId"]
    ]

    valid_credits = []
    invalid_credits = []

    for credit in credits_for_person:
        valid, _reason = credit_notes_validator.credit_notes_are_valid_for_kind(
            credit.notes, kind
        )
        if valid:
            valid_credits.append(credit)
        else:
            invalid_credits.append(credit)

    if valid_credits:
        return (False, "None")

    return (
        True,
        " / ".join(
            [
                invalid_credit.notes
                for invalid_credit in invalid_credits
                if invalid_credit.notes
            ]
        ),
    )


def get_title_ids_from_name_pages_for_credit_kind(
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    kind: imdb_http.CreditKind,
) -> set[str]:
    if isinstance(watchlist_person["imdbId"], str):
        name_page = imdb_http.get_name_page(watchlist_person["imdbId"])
        return set([credit.imdb_id for credit in name_page.credits[kind]])

    filmographies: list[set[str]] = []
    for imdb_id in watchlist_person["imdbId"]:
        name_page = imdb_http.get_name_page(imdb_id)
        filmographies.append(set(credit.imdb_id for credit in name_page.credits[kind]))

    return set.intersection(*filmographies)


def remove_watchlist_person_titles_not_in_given_title_ids(
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    credit_title_ids: set[str],
) -> None:
    for title_kind in ("titles", "excludedTitles"):
        existing_title_ids = set(
            [title["imdbId"] for title in watchlist_person[title_kind]]  # type:ignore
        )

        missing_titles = (
            title
            for title in watchlist_person["titles"]
            if title["imdbId"] in existing_title_ids - credit_title_ids
        )

        for missing_title in missing_titles:
            watchlist_person[title_kind].remove(missing_title)  # type:ignore
            logger.log(
                "Missing title {} removed from {}.", missing_title["title"], title_kind
            )


def filter_existing_titles_for_watchlist_person(
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    credit_title_ids: set[str],
) -> set[str]:
    existing_excluded_title_ids = [
        excluded_title["imdbId"]
        for excluded_title in watchlist_person["excludedTitles"]
    ]

    existing_title_ids = [title["imdbId"] for title in watchlist_person["titles"]]

    return credit_title_ids.difference(existing_excluded_title_ids).difference(
        existing_title_ids
    )


def title_page_is_invalid_credit(
    title_page: imdb_http.TitlePage,
) -> tuple[bool, str]:
    if title_page.kind not in VALID_KINDS:
        return (True, title_page.kind)

    invalid_genres = {"Adult", "Short", "Documentary"} & title_page.genres
    if invalid_genres:
        return (True, ", ".join(invalid_genres))

    if "Silent" in title_page.sound_mix:
        return (True, "silent")

    return (False, "None")


def update_watchlist_person_titles_for_credit_kind(  # noqa: WPS210, WPS231
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    kind: imdb_http.CreditKind,
) -> None:
    credit_title_ids = get_title_ids_from_name_pages_for_credit_kind(
        watchlist_person=watchlist_person, kind=kind
    )

    remove_watchlist_person_titles_not_in_given_title_ids(
        watchlist_person=watchlist_person, credit_title_ids=credit_title_ids
    )

    new_credit_title_ids = filter_existing_titles_for_watchlist_person(
        watchlist_person=watchlist_person, credit_title_ids=credit_title_ids
    )

    for index, imdb_id in enumerate(new_credit_title_ids):
        logger.log(
            "{}/{} fetching data for {}...",
            index + 1,
            len(new_credit_title_ids),
            imdb_id,
        )

        title_page = imdb_http.get_title_page(imdb_id)

        if title_page.production_status:
            logger.log(
                "Skipping {} for {} production status: {}",
                title_page.full_title,
                watchlist_person["name"],
                title_page.production_status,
            )
            continue

        title_page_is_invalid, reason = title_page_is_invalid_credit(title_page)

        if title_page_is_invalid:
            add_title_page_to_watchlist_person_excluded_titles(
                title_page=title_page,
                watchlist_person=watchlist_person,
                reason=reason,
            )
            continue

        (
            all_credits_are_invalid,
            reason,
        ) = all_credits_on_title_page_are_invalid_for_watchlist_person(
            title_page=title_page, watchlist_person=watchlist_person, kind=kind
        )
        if all_credits_are_invalid:
            add_title_page_to_watchlist_person_excluded_titles(
                title_page=title_page,
                watchlist_person=watchlist_person,
                reason=reason,
            )
            continue

        add_title_page_to_watchlist_person_titles(
            title_page=title_page, watchlist_person=watchlist_person
        )


WatchlistKindToCreditKind: dict[json_watchlist_people.Kind, imdb_http.CreditKind] = {
    "directors": "director",
    "performers": "performer",
    "writers": "writer",
}


def get_progress_file_path(kind: json_watchlist_people.Kind) -> str:
    progress_file_path = os.path.join(
        watchlist_serializer.FOLDER_PATH, kind, ".progress"
    )
    path_tools.ensure_file_path(progress_file_path)

    return progress_file_path


def update_watchlist_credits() -> None:  # noqa: WPS210, WPS231
    progress_files: list[str] = []
    for kind in json_watchlist_people.KINDS:
        processed_slugs = []

        progress_file_path = get_progress_file_path(kind)
        progress_files.append(progress_file_path)

        with open(
            progress_file_path, "r+" if os.path.exists(progress_file_path) else "w+"
        ) as progress_file:
            progress_file.seek(0)
            processed_slugs = progress_file.read().splitlines()
            for watchlist_person in json_watchlist_people.read_all(kind):
                logger.log(
                    "==== Begin getting {} credits for {}...",
                    WatchlistKindToCreditKind[kind],
                    watchlist_person["name"],
                )

                if watchlist_person["slug"] in processed_slugs:
                    logger.log(
                        "Skipping {} (already processed).",
                        watchlist_person["name"],
                    )
                    continue

                try:
                    update_watchlist_person_titles_for_credit_kind(
                        watchlist_person, WatchlistKindToCreditKind[kind]
                    )
                except imdb_http.IMDbDataAccessError:
                    return
                json_watchlist_people.serialize(watchlist_person, kind)
                progress_file.write("{0}\n".format(watchlist_person["slug"]))

    for completed_progress_file_path in progress_files:
        os.remove(completed_progress_file_path)
