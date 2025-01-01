from __future__ import annotations

import datetime
import re
import sqlite3
from contextlib import contextmanager
from os import path
from typing import Any, Callable, Dict, Generator, Tuple

from movielog.repository import api as repository_api
from movielog.utils import list_tools
from movielog.utils.logging import logger

DB_FILE_NAME = "sabren.sqlite3"
DB_DIR = "db"

Connection = sqlite3.Connection
Cursor = sqlite3.Cursor
Row = sqlite3.Row

DB_PATH = path.join(DB_DIR, DB_FILE_NAME)
DbConnectionOpts: Dict[str, Any] = {"isolation_level": None}
RowFactory = Callable[[sqlite3.Cursor, Tuple[Any, ...]], Any]


@contextmanager
def connect() -> Generator[Connection, None, None]:
    connection = sqlite3.connect(DB_PATH, **DbConnectionOpts)
    yield connection
    connection.close()


def fetch_one(query: str, row_factory: RowFactory = sqlite3.Row) -> Any:
    with connect() as connection:
        connection.row_factory = row_factory
        return connection.execute(query).fetchone()


def fetch_all(query: str, row_factory: RowFactory = sqlite3.Row) -> list[Any]:
    with connect() as connection:
        connection.row_factory = row_factory
        return connection.execute(query).fetchall()


def add_legacy_viewings() -> None:  # noqa: WPS210, WPS231
    logger.log("Initializing...")

    reviews = list_tools.list_to_dict(
        repository_api.reviews(), key=lambda review: review.imdb_id
    )

    for post_id_row in get_post_ids():
        imdb_url = None
        viewing_date = None
        imdb_id = None

        for post_meta_row in get_post_meta_for_id(post_id_row["ID"]):
            if post_meta_row["meta_key"] == "Date Viewed":
                viewing_date = post_meta_row["meta_value"]
            if post_meta_row["meta_key"] == "IMDB":
                imdb_url = post_meta_row["meta_value"]

        if imdb_url is None or viewing_date is None:
            continue

        match = re.search(r"tt\d+", imdb_url)

        if not match:
            continue

        imdb_id = match.group()

        if imdb_id == "tt0081529":
            imdb_id = "tt0076729"

        title = reviews[imdb_id].title()

        repository_api.create_viewing(
            imdb_id=imdb_id,
            full_title="{0} ({1})".format(title.title, title.year),
            date=datetime.datetime.strptime(viewing_date, "%Y-%m-%d").date(),
            medium=None,
            venue=None,
            medium_notes=None,
        )


def get_post_meta_for_id(id: str) -> Any:
    query = """
        SELECT
        *
        FROM wp_fmlpostmeta
        WHERE post_id = {0}
    """

    return fetch_all(query.format(id))


def get_post_ids() -> list[Any]:

    query = """
        SELECT
        post_title
        , id
        FROM wp_fmlposts
        WHERE post_type = 'post'
        AND post_parent = 0
        AND post_status = 'publish'
        ORDER BY id
    """

    return fetch_all(query)


if __name__ == "__main__":
    add_legacy_viewings()
