from __future__ import annotations

import os
from copy import deepcopy
from typing import TypedDict, cast

from movielog.repository import credit_notes_validator, imdb_http, json_titles
from movielog.repository.datasets import api as datasets_api
from movielog.repository.db import api as db_api
from movielog.utils import path_tools
from movielog.utils.logging import logger

FrozenTitles = set("tt2166834")

ValidTitles = {
    "tt0064727": "The Bloody Judge",
    "tt0065036": "Stereo (Tile 3B of a CAEE Educational Mosaic)",
    "tt0094762": "Blood Delirium",
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
        db_api.db.fetch_one(query.format(json_title["imdbId"])),  # noqa: WPS204
    )

    assert title_row

    json_title["title"] = title_row["title"]
    json_title["originalTitle"] = title_row["original_title"]
    json_title["year"] = str(title_row["year"])
    json_title["sortTitle"] = json_titles.generate_sort_title(
        json_title["title"], json_title["year"]
    )
    json_title["runtimeMinutes"] = title_row["runtime_minutes"] or 0


def _update_json_title_with_title_page_data(json_title: json_titles.JsonTitle) -> None:
    imdb_title_page = imdb_http.get_title_page(json_title["imdbId"])

    json_title["releaseDate"] = imdb_title_page.release_date
    json_title["countries"] = imdb_title_page.countries
    json_title["genres"] = imdb_title_page.genres
    json_title["directors"] = [
        json_titles.JsonDirector(
            imdbId=director.imdb_id,
            name=director.name,
        )
        for director in imdb_title_page.credits["director"]
        if credit_notes_validator.credit_notes_are_valid_for_kind(director.notes, "director")[0]
    ]

    json_title["performers"] = [
        json_titles.JsonPerformer(
            imdbId=performer.imdb_id,
            name=performer.name,
            roles=performer.roles,
        )
        for performer in imdb_title_page.credits["performer"]
        if credit_notes_validator.credit_notes_are_valid_for_kind(performer.notes, "performer")[0]
    ]
    json_title["writers"] = [
        json_titles.JsonWriter(
            imdbId=writer.imdb_id,
            name=writer.name,
            notes=writer.notes,
        )
        for writer in imdb_title_page.credits["writer"]
        if credit_notes_validator.credit_notes_are_valid_for_kind(writer.notes, "writer")[0]
    ]


def _get_progress_file_path() -> str:
    progress_file_path = os.path.join(json_titles.FOLDER_NAME, ".progress")
    path_tools.ensure_file_path(progress_file_path)

    return progress_file_path


def update_from_imdb_pages() -> None:  # noqa: WPS210, WPS231
    processed_slugs = []
    progress_file_path = _get_progress_file_path()

    with open(
        progress_file_path, "r+" if os.path.exists(progress_file_path) else "w+"
    ) as progress_file:
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

            try:
                _update_json_title_with_title_page_data(updated_title)
            except imdb_http.IMDbDataAccessError:
                return
            if updated_title != json_title:
                json_titles.serialize(updated_title)
            progress_file.write("{0}\n".format(json_title["slug"]))

    os.remove(progress_file_path)


def update_title(json_title: json_titles.JsonTitle) -> None:
    if json_title["imdbId"] in FrozenTitles:
        return

    updated_json_title = deepcopy(json_title)
    _update_json_title_with_db_data(updated_json_title)
    _update_json_title_with_title_page_data(updated_json_title)

    if updated_json_title != json_title:
        json_titles.serialize(updated_json_title)


def update_for_datasets(  # noqa: WPS231
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
