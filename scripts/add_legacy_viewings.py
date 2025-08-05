from __future__ import annotations

import datetime
import re
import sqlite3
import types
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from movielog.repository import api as repository_api
from movielog.utils import list_tools
from movielog.utils.logging import logger

DB_FILE_NAME = "sabren.sqlite3"
DB_DIR = "db"

Connection = sqlite3.Connection
Cursor = sqlite3.Cursor
Row = sqlite3.Row

DB_PATH = Path(DB_DIR) / DB_FILE_NAME
DbConnectionOpts: dict[str, Any] = {"isolation_level": None}
RowFactory = Callable[[sqlite3.Cursor, tuple[Any, ...]], Any]

SLUG_MAP = types.MappingProxyType(
    {
        "anchorman-2004": "anchorman-the-legend-of-ron-burgundy-2004",
        "blowup-1966": "blow-up-1966",
        "bowling-for-columbine-2002": None,
        "christmas-vacation-1989": "national-lampoons-christmas-vacation-1989",
        "crash-1996i": "crash-1996",
        "curse-of-the-crimson-altar-1968": "the-crimson-cult-1968",
        "devils-playground-2002": None,
        "dogtown-and-z-boys-2001": None,
        "dracula-1958": "horror-of-dracula-1958",
        "harold-kumar-go-to-white-castle-2004": "harold-and-kumar-go-to-white-castle-2004",
        "matthew-hopkins-witchfinder-general-1968": "witchfinder-general-1968",
        "sha-ren-zhe-tang-zhan-1993": "the-assassin-1993",
        "sydney-1996": "hard-eight-1996",
        "taste-of-fear-1961": "scream-of-fear-1961",
        "the-era-of-vampire-2002": "vampire-hunters-2003",
        "the-seven-brothers-meet-dracula-1979": "the-legend-of-the-7-golden-vampires-1974",
        "the-stranglers-of-bombay-1960": "the-stranglers-of-bombay-1959",
        "vampira-1974": "old-dracula-1974",
    }
)


@contextmanager
def connect() -> Generator[Connection]:
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


def add_legacy_viewings() -> None:  # noqa: C901
    logger.log("Initializing...")

    reviews = list_tools.list_to_dict(repository_api.reviews(), key=lambda review: review.slug)

    for post_id_row in get_post_ids():
        viewing_dates = [
            post_meta_row
            for post_meta_row in get_post_meta_for_id(post_id_row["ID"])
            if post_meta_row["meta_key"] == "Date Viewed"
        ]

        if len(viewing_dates) == 0:
            raise Exception(  # noqa: TRY002
                "No viewings for {} [{}]".format(post_id_row["post_name"], post_id_row["ID"])
            )

        slug = post_id_row["post_name"]

        match_the = re.search(r"-the-(\d{4})$", slug)

        if match_the:
            slug = "the-{}".format(re.sub(r"the-(\d{4})$", match_the.groups()[0], slug))

        match_a = re.search(r"-a-(\d{4})$", slug)

        if match_a:
            slug = "a-{}".format(re.sub(r"a-(\d{4})$", match_a.groups()[0], slug))

        if slug in SLUG_MAP:
            slug = SLUG_MAP[slug]

        if slug is None:
            logger.log("Skipping {0}...", post_id_row["post_name"])
            continue

        title = reviews[slug].title()

        for viewing_date in viewing_dates:
            repository_api.create_viewing(
                imdb_id=title.imdb_id,
                full_title=f"{title.title} ({title.release_year})",
                date=datetime.datetime.fromisoformat(viewing_date).date(),
                medium=None,
                venue=None,
                medium_notes=None,
            )


def get_post_meta_for_id(post_id: str) -> Any:
    query = """
        SELECT
        *
        FROM wp_postmeta
        WHERE post_id = {0}
    """

    return fetch_all(query.format(post_id))


def get_post_ids() -> list[Any]:
    query = """
        SELECT
        *
        FROM wp_posts
        JOIN wp_post2cat ON wp_post2cat.post_id = wp_posts.ID
        WHERE wp_post2cat.category_id = '13'
        AND post_status = 'publish'
        ORDER BY post_date;
    """

    return fetch_all(query)


if __name__ == "__main__":
    add_legacy_viewings()
