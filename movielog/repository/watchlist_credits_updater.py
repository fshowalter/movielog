from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from movielog.repository import (
    credit_notes_validator,
    imdb_http_person,
    imdb_http_title,
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


def _add_title_page_to_watchlist_person_excluded_titles(
    title_page: imdb_http_title.TitlePage,
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


def _add_title_page_to_watchlist_person_titles(
    title_page: imdb_http_title.TitlePage,
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


def _all_credits_on_title_page_are_invalid_for_watchlist_person(
    title_page: imdb_http_title.TitlePage,
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    kind: imdb_http_title.CreditKind,
) -> tuple[bool, str]:
    credits_for_person = [
        credit
        for credit in title_page.credits[kind]
        if credit.imdb_id == watchlist_person["imdbId"]
    ]

    valid_credits = []
    invalid_credits = []

    for credit in credits_for_person:
        valid, _reason = credit_notes_validator.credit_notes_are_valid_for_kind(credit.notes, kind)
        if valid:
            valid_credits.append(credit)
        else:
            invalid_credits.append(credit)

    if valid_credits:
        return (False, "None")

    return (
        True,
        " / ".join(
            [invalid_credit.notes for invalid_credit in invalid_credits if invalid_credit.notes]
        ),
    )


def _get_title_ids_from_name_pages_for_credit_kind(
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    kind: imdb_http_title.CreditKind,
) -> set[str]:
    if isinstance(watchlist_person["imdbId"], str):
        name_page = imdb_http_person.get_name_page(watchlist_person["imdbId"])
        print(name_page)
        return {credit.imdb_id for credit in name_page.credits[kind]}

    filmographies: list[set[str]] = []
    for imdb_id in watchlist_person["imdbId"]:
        name_page = imdb_http_person.get_name_page(imdb_id)
        filmographies.append({credit.imdb_id for credit in name_page.credits[kind]})

    return set.intersection(*filmographies)


def _remove_watchlist_person_titles_not_in_given_title_ids(
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    credit_title_ids: set[str],
) -> None:
    for title_kind in ("titles", "excludedTitles"):
        existing_title_ids = {title["imdbId"] for title in watchlist_person[title_kind]}

        missing_titles = (
            title
            for title in watchlist_person["titles"]
            if title["imdbId"] in existing_title_ids - credit_title_ids
        )

        for missing_title in missing_titles:
            watchlist_person[title_kind].remove(missing_title)  # type:ignore
            logger.log("Missing title {} removed from {}.", missing_title["title"], title_kind)


def _filter_existing_titles_for_watchlist_person(
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    credit_title_ids: set[str],
) -> set[str]:
    existing_excluded_title_ids = [
        excluded_title["imdbId"] for excluded_title in watchlist_person["excludedTitles"]
    ]

    existing_title_ids = [title["imdbId"] for title in watchlist_person["titles"]]

    return credit_title_ids.difference(existing_excluded_title_ids).difference(existing_title_ids)


def _title_page_is_invalid_credit(
    title_page: imdb_http_title.TitlePage,
) -> tuple[bool, str]:
    if title_page.kind not in VALID_KINDS:
        return (True, title_page.kind)

    invalid_genres = {"Adult", "Short", "Documentary"} & set(title_page.genres)
    if invalid_genres:
        return (True, ", ".join(invalid_genres))

    if "Silent" in title_page.sound_mix:
        return (True, "silent")

    return (False, "None")


def _update_watchlist_person_titles_for_credit_kind(
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    kind: imdb_http_title.CreditKind,
) -> None:
    credit_title_ids = _get_title_ids_from_name_pages_for_credit_kind(
        watchlist_person=watchlist_person, kind=kind
    )

    _remove_watchlist_person_titles_not_in_given_title_ids(
        watchlist_person=watchlist_person, credit_title_ids=credit_title_ids
    )

    new_credit_title_ids = _filter_existing_titles_for_watchlist_person(
        watchlist_person=watchlist_person, credit_title_ids=credit_title_ids
    )

    for index, imdb_id in enumerate(new_credit_title_ids):
        logger.log(
            "{}/{} fetching data for {}...",
            index + 1,
            len(new_credit_title_ids),
            imdb_id,
        )

        title_page = imdb_http_title.get_title_page(imdb_id)

        if title_page.production_status:
            logger.log(
                "Skipping {} for {} production status: {}",
                title_page.full_title,
                watchlist_person["name"],
                title_page.production_status,
            )
            continue

        title_page_is_invalid, reason = _title_page_is_invalid_credit(title_page)

        if title_page_is_invalid:
            _add_title_page_to_watchlist_person_excluded_titles(
                title_page=title_page,
                watchlist_person=watchlist_person,
                reason=reason,
            )
            continue

        (
            all_credits_are_invalid,
            reason,
        ) = _all_credits_on_title_page_are_invalid_for_watchlist_person(
            title_page=title_page, watchlist_person=watchlist_person, kind=kind
        )
        if all_credits_are_invalid:
            _add_title_page_to_watchlist_person_excluded_titles(
                title_page=title_page,
                watchlist_person=watchlist_person,
                reason=reason,
            )
            continue

        _add_title_page_to_watchlist_person_titles(
            title_page=title_page, watchlist_person=watchlist_person
        )

    watchlist_person["titles"] = sorted(
        watchlist_person["titles"], key=json_watchlist_people.title_sort_key
    )

    watchlist_person["excludedTitles"] = sorted(
        watchlist_person["excludedTitles"], key=json_watchlist_people.title_sort_key
    )


WatchlistKindToCreditKind: dict[json_watchlist_people.Kind, imdb_http_title.CreditKind] = {
    "directors": "director",
    "performers": "performer",
    "writers": "writer",
}


def _get_progress_file_path(kind: json_watchlist_people.Kind) -> Path:
    progress_file_path = Path(watchlist_serializer.FOLDER_NAME) / kind / ".progress"

    path_tools.ensure_file_path(progress_file_path)

    return progress_file_path


def update_watchlist_credits() -> None:
    progress_files: list[Path] = []
    for kind in json_watchlist_people.KINDS:
        processed_slugs = []

        progress_file_path = _get_progress_file_path(kind)
        progress_files.append(progress_file_path)

        with Path.open(
            progress_file_path, "r+" if progress_file_path.exists() else "w+"
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

                updated_watchlist_person = deepcopy(watchlist_person)

                _update_watchlist_person_titles_for_credit_kind(
                    updated_watchlist_person, WatchlistKindToCreditKind[kind]
                )

                if updated_watchlist_person != watchlist_person:
                    json_watchlist_people.serialize(updated_watchlist_person, kind)
                progress_file.write("{}\n".format(watchlist_person["slug"]))

    for completed_progress_file_path in progress_files:
        Path.unlink(completed_progress_file_path)
