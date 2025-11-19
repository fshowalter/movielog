from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from movielog.repository import (
    imdb_http_director,
    imdb_http_performer,
    imdb_http_writer,
    json_watchlist_people,
    watchlist_serializer,
)
from movielog.repository.imdb_http_person import CreditKind, TitleCredit
from movielog.repository.json_watchlist_titles import JsonWatchlistTitle
from movielog.utils import path_tools
from movielog.utils.logging import logger


def _add_title_page_to_watchlist_person_titles(
    title_credit: TitleCredit,
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
) -> None:
    watchlist_person["titles"].append(
        JsonWatchlistTitle(
            imdbId=title_credit.imdb_id,
            title=title_credit.full_title,
            titleType=title_credit.title_type,
            attributes=title_credit.attributes,
            role=title_credit.role,
        )
    )

    logger.log(
        "{} added to {}.",
        title_credit.full_title,
        "titles",
    )


def _get_title_credits_from_name_pages_for_credit_kind(
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    kind: CreditKind,
) -> set[TitleCredit]:
    method_map = {
        "director": imdb_http_director.get_director,
        "writer": imdb_http_writer.get_writer,
        "performer": imdb_http_performer.get_performer,
    }

    if isinstance(watchlist_person["imdbId"], str):
        person = method_map[kind](watchlist_person["imdbId"])
        return set(person.credits)

    filmographies: list[set[TitleCredit]] = []
    for imdb_id in watchlist_person["imdbId"]:
        person = method_map[kind](imdb_id)
        filmographies.append(set(person.credits))

    return set.intersection(*filmographies)


def _remove_watchlist_person_titles_not_in_given_title_credits(
    watchlist_person: json_watchlist_people.JsonWatchlistPerson, title_credits: set[TitleCredit]
) -> None:
    for title_kind in ("titles", "excludedTitles"):
        existing_title_ids = {title["imdbId"] for title in watchlist_person[title_kind]}

        missing_titles = (
            title
            for title in watchlist_person["titles"]
            if title["imdbId"] in existing_title_ids - {credit.imdb_id for credit in title_credits}
        )

        for missing_title in missing_titles:
            watchlist_person[title_kind].remove(missing_title)
            logger.log("Missing title {} removed from {}.", missing_title["title"], title_kind)


def _filter_existing_titles_for_watchlist_person(
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    title_credits: set[TitleCredit],
) -> set[TitleCredit]:
    existing_excluded_title_ids = {
        excluded_title["imdbId"] for excluded_title in watchlist_person["excludedTitles"]
    }

    existing_title_ids = {title["imdbId"] for title in watchlist_person["titles"]}

    return {
        credit
        for credit in title_credits
        if credit.imdb_id not in existing_title_ids
        and credit.imdb_id not in existing_excluded_title_ids
    }


def _update_watchlist_person_titles_for_credit_kind(
    watchlist_person: json_watchlist_people.JsonWatchlistPerson,
    kind: CreditKind,
) -> None:
    title_credits = _get_title_credits_from_name_pages_for_credit_kind(
        watchlist_person=watchlist_person, kind=kind
    )

    _remove_watchlist_person_titles_not_in_given_title_credits(
        watchlist_person=watchlist_person, title_credits=title_credits
    )

    new_title_credits = _filter_existing_titles_for_watchlist_person(
        watchlist_person=watchlist_person, title_credits=title_credits
    )

    for index, title_credit in enumerate(new_title_credits):
        logger.log(
            "{}/{} fetching data for {}...",
            index + 1,
            len(new_title_credits),
            title_credit.imdb_id,
        )

        _add_title_page_to_watchlist_person_titles(
            title_credit=title_credit, watchlist_person=watchlist_person
        )

    watchlist_person["titles"] = sorted(
        watchlist_person["titles"], key=json_watchlist_people.title_sort_key
    )

    watchlist_person["excludedTitles"] = sorted(
        watchlist_person["excludedTitles"], key=json_watchlist_people.title_sort_key
    )


WatchlistKindToCreditKind: dict[json_watchlist_people.Kind, CreditKind] = {
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
