from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import cast

from movielog.repository import (
    json_collections,
    json_titles,
    json_watchlist_people,
    markdown_reviews,
    markdown_viewings,
    title_data_updater,
)
from movielog.utils.logging import logger

ValidTitles = {
    "tt0064727": "The Bloody Judge",
    "tt0065036": "Stereo (Tile 3B of a CAEE Educational Mosaic)",
    "tt0094762": "Blood Delirium",
}


def _get_valid_title_ids() -> set[str]:
    title_ids = [
        *[viewing["imdbId"] for viewing in markdown_viewings.read_all()],
        *[
            title["imdbId"]
            for collection in json_collections.read_all()
            for title in collection["titles"]
        ],
        *get_review_ids(),
    ]

    for kind in json_watchlist_people.KINDS:
        for json_watchlist_person in json_watchlist_people.read_all(kind):
            title_ids = title_ids + [title["imdbId"] for title in json_watchlist_person["titles"]]

    return set(title_ids)


def validate_sort_title(json_title: json_titles.JsonTitle) -> None:
    correct_sort_title = json_titles.generate_sort_title(json_title["title"], json_title["year"])

    existing_sort_title = json_title["sortTitle"]

    if existing_sort_title == correct_sort_title:
        return

    json_title["sortTitle"] = correct_sort_title
    logger.log(
        "{} ({}) [{}]: sortTitle was {} corrected to {}.",
        json_title["title"],
        json_title["year"],
        json_title["imdbId"],
        existing_sort_title,
        json_title["sortTitle"],
    )


def validate_slug(json_title: json_titles.JsonTitle, review_ids: set[str]) -> None:
    correct_slug = json_titles.generate_title_slug(json_title["title"], json_title["year"])

    existing_slug = json_title["slug"]

    if existing_slug == correct_slug:
        return

    if json_title["imdbId"] in review_ids:
        logger.log(
            "Reviewed title {} ({}) [{}]: slug is {} but should be {}. {}",
            json_title["title"],
            json_title["year"],
            json_title["imdbId"],
            existing_slug,
            correct_slug,
            "REVIEW",
        )
        return

    old_slug = json_title["slug"]
    json_title["slug"] = correct_slug
    logger.log(
        "{} ({}) [{}]: slug was {} corrected to {}.",
        json_title["title"],
        json_title["year"],
        json_title["imdbId"],
        old_slug,
        json_title["slug"],
    )


def get_review_ids() -> set[str]:
    return {review.yaml["imdb_id"] for review in markdown_reviews.read_all()}


def add_new_titles(token: str, new_title_ids: set[str]) -> None:
    watchlist_performer_ids = {
        performer["imdbId"]
        for performer in json_watchlist_people.read_all("performers")
        if not isinstance(performer["imdbId"], list)
    }

    for index, title_id_to_add in enumerate(new_title_ids):
        logger.log(
            "{}/{} adding title {}...",
            index + 1,
            len(new_title_ids),
            title_id_to_add,
        )

        new_title = json_titles.JsonTitle(
            imdbId=title_id_to_add,
            title="",
            originalTitle="",
            sortTitle="",
            year="",
            slug="",
            releaseDate="????",
            releaseDateCountry="",
            runtimeMinutes=0,
            countries=[],
            genres=[],
            directors=[],
            performers=[],
            writers=[],
        )

        title_data_updater.update_title(token, new_title, watchlist_performer_ids)


def removed_files_marked_for_removal(files_marked_for_removal: list[Path]) -> None:
    for file_path_to_remove in files_marked_for_removal:
        Path.unlink(Path(file_path_to_remove))
        logger.log(
            "{0} removed.",
            file_path_to_remove,
        )


def rename_files_marked_for_rename(files_marked_for_rename: list[tuple[Path, Path]]) -> None:
    for old_file_path, new_file_path in files_marked_for_rename:
        Path.rename(old_file_path, new_file_path)
        logger.log("{0} renamed to {1}.", old_file_path, new_file_path)


def validate(token: str) -> None:
    title_ids_to_process = _get_valid_title_ids()
    files_to_remove = []
    files_to_rename = []

    review_ids = get_review_ids()

    for file_path in Path(json_titles.FOLDER_NAME).glob("*.json"):
        with Path.open(file_path, "r+") as json_file:
            json_title = cast(json_titles.JsonTitle, json.load(json_file))

            if json_title["imdbId"] not in title_ids_to_process:
                logger.log(
                    "{} ({}) [{}] not found in viewings or watchlist. {}",
                    json_title["title"],
                    json_title["year"],
                    json_title["imdbId"],
                    "Marked for removal.",
                )
                files_to_remove.append(file_path)
                continue

            updated_title = deepcopy(json_title)

            validate_slug(updated_title, review_ids)
            validate_sort_title(updated_title)

            correct_file_path = json_titles.generate_file_path(updated_title)

            if file_path != correct_file_path:
                files_to_rename.append((file_path, correct_file_path))
                logger.log(
                    "{} filename should be {}. {}",
                    file_path,
                    correct_file_path,
                    "Marked for rename.",
                )

            if json_title != updated_title:
                json_file.seek(0)
                json_file.write(
                    json.dumps(updated_title, default=str, indent=2, ensure_ascii=False)
                )
                json_file.truncate()
                logger.log(
                    "Wrote {}.",
                    file_path,
                )

            title_ids_to_process.remove(json_title["imdbId"])

    removed_files_marked_for_removal(files_to_remove)

    rename_files_marked_for_rename(files_to_rename)

    add_new_titles(token, title_ids_to_process)
