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


def add_legacy_reviews() -> None:  # noqa: WPS210, WPS231
    logger.log("Initializing...")

    reviews = list_tools.list_to_dict(
        repository_api.reviews(), key=lambda review: review.slug
    )

    for review_row in get_review_rows():
        viewing_dates = []
        slug = review_row["post_name"]

        match = re.search(r".*-(.*)-\d{4}", slug)

        if match:
            last_word = match.groups()[0]

            if last_word in ["the", "a"]:
                slug = "{0}-{1}".format(
                    last_word, slug.replace("-{0}-".format(last_word), "-")
                )

        if slug in reviews.keys():
            continue

        logger.log(slug)
        continue

        for post_meta_row in get_post_meta_for_id(review_row["ID"]):
            for key in post_meta_row.keys():
                "{0}:{1}".format(key, post_meta_row[key])
            if post_meta_row["meta_key"] == "Date Viewed":
                viewing_dates.append(post_meta_row["meta_value"])

        title = reviews[slug].title()

        logger.log(viewing_dates[-1])

        for viewing_date in viewing_dates:
            repository_api.create_viewing(
                imdb_id=title.imdb_id,
                full_title="{0} ({1})".format(title.title, title.year),
                date=datetime.datetime.fromisoformat(viewing_date).date(),
                medium=None,
                venue=None,
                medium_notes=None,
            )


def get_post_meta_for_id(id: str) -> Any:
    query = """
        SELECT
        *
        FROM wp_postmeta
        WHERE post_id = {0}
    """

    return fetch_all(query.format(id))


def get_review_rows() -> list[Any]:

    query = """
        SELECT
        post_title
        , post_name
        , id
        FROM wp_posts
        JOIN wp_post2cat ON wp_post2cat.post_id = wp_posts.ID
        WHERE wp_post2cat.category_id = '13'
        AND post_status = 'publish'
        ORDER BY post_date;
    """

    return fetch_all(query)


if __name__ == "__main__":
    add_legacy_reviews()
