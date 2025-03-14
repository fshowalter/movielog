from __future__ import annotations

import datetime
import re
import sqlite3
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import yaml

from movielog.repository import api as repository_api
from movielog.utils import list_tools, path_tools
from movielog.utils.logging import logger

FOLDER_NAME = "reviews"
DB_FILE_NAME = "sabren.sqlite3"
DB_DIR = "db"

Connection = sqlite3.Connection
Cursor = sqlite3.Cursor
Row = sqlite3.Row

DB_PATH = Path(DB_DIR) / DB_FILE_NAME
DbConnectionOpts: dict[str, Any] = {"isolation_level": None}
RowFactory = Callable[[sqlite3.Cursor, tuple[Any, ...]], Any]


def _represent_none(self: Any, _: Any) -> Any:
    return self.represent_scalar("tag:yaml.org,2002:null", "")


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


def _generate_file_path(slug: str) -> Path:
    file_path = Path(FOLDER_NAME) / f"{slug}.md"

    path_tools.ensure_file_path(file_path)

    return file_path


def create_review(
    slug: str, date: datetime.date, review_content: str, grade: str
) -> Path:
    yaml.add_representer(type(None), _represent_none)

    file_path = _generate_file_path(slug)

    stripped_content = str(review_content or "").strip()

    with Path.open(file_path, "w") as output_file:
        output_file.write("---\n")
        yaml.dump(
            {
                "imdb_id": None,
                "slug": slug,
                "grade": grade,
                "date": date,
            },
            encoding="utf-8",
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            stream=output_file,
        )
        output_file.write("---\n\n")
        output_file.write(stripped_content)

    logger.log("Wrote {}", file_path)

    return file_path


def add_legacy_reviews() -> None:  # noqa: C901
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
                stripped_article = slug.replace(f"-{last_word}-", "-")
                slug = f"{last_word}-{stripped_article}"

        if slug in reviews:
            continue

        for post_meta_row in get_post_meta_for_id(review_row["ID"]):
            for key in post_meta_row:
                f"{key}:{post_meta_row[key]}"
            if post_meta_row["meta_key"] == "Date Viewed":
                viewing_dates.append(post_meta_row["meta_value"])
            if post_meta_row["meta_key"] == "Grade":
                grade = post_meta_row["meta_value"]

        create_review(
            slug=slug,
            date=datetime.datetime.fromisoformat(viewing_dates[-1]).date(),
            review_content=review_row["post_content"],
            grade=grade,
        )


def get_post_meta_for_id(post_id: str) -> Any:
    query = """
        SELECT
        *
        FROM wp_postmeta
        WHERE post_id = {0}
    """

    return fetch_all(query.format(post_id))


def get_review_rows() -> list[Any]:
    query = """
        SELECT
        post_title
        , post_content
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
