from __future__ import annotations

import os

from movielog.repository import credit_notes_validator, imdb_http, json_titles
from movielog.utils import path_tools
from movielog.utils.logging import logger


def update_json_title(json_title: json_titles.JsonTitle) -> None:
    imdb_title_page = imdb_http.get_title_page(json_title["imdbId"])

    json_title["countries"] = list(imdb_title_page.countries)
    json_title["genres"] = list(imdb_title_page.genres)
    json_title["directors"] = [
        json_titles.JsonDirector(
            imdbId=director.imdb_id,
            name=director.name,
            sequence=director.sequence,
        )
        for director in imdb_title_page.credits["director"]
        if credit_notes_validator.credit_notes_are_valid_for_kind(
            director.notes, "director"
        )[0]
    ]

    json_title["performers"] = [
        json_titles.JsonPerformer(
            imdbId=performer.imdb_id,
            name=performer.name,
            sequence=performer.sequence,
            roles=performer.roles,
        )
        for performer in imdb_title_page.credits["performer"]
        if credit_notes_validator.credit_notes_are_valid_for_kind(
            performer.notes, "performer"
        )[0]
    ]
    json_title["writers"] = [
        json_titles.JsonWriter(
            imdbId=writer.imdb_id,
            name=writer.name,
            sequence=writer.sequence,
            notes=writer.notes,
        )
        for writer in imdb_title_page.credits["writer"]
        if credit_notes_validator.credit_notes_are_valid_for_kind(
            writer.notes, "writer"
        )[0]
    ]


def get_progress_file_path() -> str:
    progress_file_path = os.path.join(json_titles.FOLDER_NAME, ".progress")
    path_tools.ensure_file_path(progress_file_path)

    return progress_file_path


def update_title_data() -> None:  # noqa: WPS210, WPS231
    processed_slugs = []
    progress_file_path = get_progress_file_path()

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

            try:
                update_json_title(json_title)
            except imdb_http.IMDbDataAccessError:
                return
            json_titles.serialize(json_title)
            progress_file.write("{0}\n".format(json_title["slug"]))

    os.remove(progress_file_path)
