from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import TypedDict, cast

from movielog.repository import (
    imdb_http_title,
    json_imdb_ratings,
    json_titles,
    json_watchlist_people,
)
from movielog.repository.datasets import api as datasets_api
from movielog.repository.db import api as db_api
from movielog.utils import path_tools
from movielog.utils.logging import logger

AllowedArchiveFootageTitles = {
    "tt0839995",  # Superman II: The Richard Donner Cut
    "tt10045260",  # Exorcist III: Legion
    "tt6019206",  # Kill Bill: The Whole Bloody Affair
    "tt3420392",  # The House of Exorcism
}

FrozenTitles = {
    "tt2166834": "Batman: The Dark Knight Returns",
    "tt0839995": "Superman II: The Richard Donner Cut",
}

ValidTitles = {
    "tt0064727": "The Bloody Judge",
    "tt0065036": "Stereo (Tile 3B of a CAEE Educational Mosaic)",
    "tt0094762": "Blood Delirium",
    "tt0040068": "Abbott and Costello Meet Frankenstein",
    "tt0103874": "Bram Stoker's Dracula",
    "tt0053719": "The City of the Dead",
    "tt0103743": "The Untold Story",
}


class TitleQueryResult(TypedDict):
    title: str
    original_title: str
    year: int
    runtime_minutes: int | None


def _update_json_title_with_db_data(json_title: json_titles.JsonTitle) -> None:
    query = """
        SELECT
            title
        , original_title
        , year
        , runtime_minutes
        FROM titles
        WHERE imdb_id = "{0}";
    """

    title_row = cast(
        TitleQueryResult,
        db_api.db.fetch_one(query.format(json_title["imdbId"])),
    )

    assert title_row

    json_title["title"] = title_row["title"]
    json_title["originalTitle"] = title_row["original_title"]
    json_title["year"] = str(title_row["year"])
    json_title["sortTitle"] = json_titles.generate_sort_title(
        json_title["title"], json_title["year"]
    )
    json_title["runtimeMinutes"] = title_row["runtime_minutes"] or 0


def _build_json_performer(performer: imdb_http_title.NameCredit) -> json_titles.JsonPerformer:
    json_performer = json_titles.JsonPerformer(
        imdbId=performer.imdb_id,
        name=performer.name,
        roles=performer.roles,
    )

    if performer.notes:
        json_performer["notes"] = performer.notes

    return json_performer


def _build_json_director(director: imdb_http_title.NameCredit) -> json_titles.JsonDirector:
    json_director = json_titles.JsonDirector(
        imdbId=director.imdb_id,
        name=director.name,
    )

    if director.notes:
        json_director["notes"] = director.notes

    return json_director


def _build_json_writer(writer: imdb_http_title.NameCredit) -> json_titles.JsonWriter:
    json_writer = json_titles.JsonWriter(
        imdbId=writer.imdb_id,
        name=writer.name,
    )

    if writer.notes:
        json_writer["notes"] = writer.notes

    return json_writer


def _update_json_title_with_title_page_data(
    json_title: json_titles.JsonTitle,
    title_page: imdb_http_title.TitlePage,
    watchlist_performer_ids: set[str],
) -> None:
    if json_title["imdbId"] not in ValidTitles:
        json_title["title"] = title_page.title

    json_title["originalTitle"] = title_page.original_title
    json_title["year"] = str(title_page.year)
    json_title["sortTitle"] = json_titles.generate_sort_title(
        json_title["title"], json_title["year"]
    )
    json_title["runtimeMinutes"] = title_page.runtime_minutes

    json_title["releaseDate"] = title_page.release_date
    json_title["countries"] = title_page.countries
    json_title["genres"] = title_page.genres
    json_title["directors"] = [
        _build_json_director(director) for director in title_page.credits["director"]
    ]

    json_title["performers"] = [
        _build_json_performer(performer)
        for performer in title_page.credits["performer"]
        if _credit_notes_are_valid_for_performer(
            imdb_title_id=json_title["imdbId"],
            imdb_person_id=performer.imdb_id,
            notes=performer.notes,
            watchlist_performer_ids=watchlist_performer_ids,
        )
    ]
    json_title["writers"] = [
        _build_json_writer(writer)
        for writer in title_page.credits["writer"]
        if _credit_notes_are_valid_for_writer(writer.notes)
    ]


def _credit_notes_are_valid_for_performer(
    imdb_title_id: str, imdb_person_id: str, notes: str | None, watchlist_performer_ids: set[str]
) -> bool:
    if not notes:
        return True

    return (
        (("archive footage" not in notes) or (imdb_title_id in AllowedArchiveFootageTitles))
        and (("uncredited" not in notes) or (imdb_person_id in watchlist_performer_ids))
        and ("scenes deleted" not in notes)
        and ("based on the comics by" not in notes)
        and ("based on the Marvel comics by" not in notes)
    )


def _credit_notes_are_valid_for_writer(notes: str | None) -> bool:
    if not notes:
        return True

    return "character" not in notes.lower()


def _get_progress_file_path() -> Path:
    progress_file_path = Path(json_titles.FOLDER_NAME) / ".progress"
    path_tools.ensure_file_path(progress_file_path)

    return progress_file_path


def update_from_imdb_pages() -> None:
    processed_slugs = []
    progress_file_path = _get_progress_file_path()

    watchlist_performer_ids = {
        performer["imdbId"]
        for performer in json_watchlist_people.read_all("performers")
        if not isinstance(performer["imdbId"], list)
    }

    ratings = json_imdb_ratings.deserialize()

    with (
        Path.open(
            progress_file_path, "r+" if progress_file_path.exists() else "w+"
        ) as progress_file,
    ):
        progress_file.seek(0)
        processed_slugs = progress_file.read().splitlines()

        titles = list(json_titles.read_all())
        total_count = len(titles)

        for index, json_title in enumerate(titles):
            if json_title["slug"] in processed_slugs:
                logger.log(
                    "{}/{} Skipped {} (already processed).",
                    index + 1,
                    total_count,
                    json_title["slug"],
                )
                continue

            logger.log(
                "{}/{} Begin processing {}...",
                index + 1,
                total_count,
                json_title["slug"],
            )

            if json_title["imdbId"] in FrozenTitles:
                continue

            updated_title = deepcopy(json_title)

            title_page = imdb_http_title.get_title_page(json_title["imdbId"])
            _update_json_title_with_title_page_data(
                updated_title, title_page, watchlist_performer_ids
            )

            ratings["titles"][title_page.imdb_id] = json_imdb_ratings.JsonRating(
                votes=title_page.vote_count, rating=title_page.aggregate_rating
            )

            if updated_title != json_title:
                json_titles.serialize(updated_title)

            json_imdb_ratings.serialize(ratings)
            progress_file.write("{}\n".format(json_title["slug"]))

    Path.unlink(progress_file_path)


def update_title(json_title: json_titles.JsonTitle, watchlist_performer_ids: set[str]) -> None:
    if json_title["imdbId"] in FrozenTitles:
        return

    updated_json_title = deepcopy(json_title)
    _update_json_title_with_db_data(updated_json_title)
    title_page = imdb_http_title.get_title_page(json_title["imdbId"])
    _update_json_title_with_title_page_data(updated_json_title, title_page, watchlist_performer_ids)

    if updated_json_title != json_title:
        json_titles.serialize(updated_json_title)


def update_for_datasets(
    dataset_titles: dict[str, datasets_api.DatasetTitle],
) -> None:
    for json_title in json_titles.read_all():
        if json_title["imdbId"] in FrozenTitles:
            continue

        dataset_title = dataset_titles.get(json_title["imdbId"], None)
        if not dataset_title:
            logger.log(
                "No dataset title found for {} ({}).",
                json_title["imdbId"],
                json_title["title"],
            )
            continue

        updated_json_title = deepcopy(json_title)

        if json_title["imdbId"] not in ValidTitles:
            updated_json_title["title"] = dataset_title["title"]

        updated_json_title["originalTitle"] = dataset_title["original_title"]
        updated_json_title["year"] = dataset_title["year"]
        updated_json_title["sortTitle"] = json_titles.generate_sort_title(
            updated_json_title["title"], updated_json_title["year"]
        )
        updated_json_title["runtimeMinutes"] = dataset_title["runtime_minutes"] or 0

        if updated_json_title != json_title:
            json_titles.serialize(updated_json_title)
