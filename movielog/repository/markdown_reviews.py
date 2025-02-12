from __future__ import annotations

import datetime
import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from glob import glob
from typing import Any, TypedDict, cast

import yaml

from movielog.repository import slugifier
from movielog.utils import path_tools
from movielog.utils.logging import logger

FOLDER_NAME = "reviews"

FM_REGEX = re.compile(r"^-{3,}\s*$", re.MULTILINE)


def _represent_none(self: Any, _: Any) -> Any:
    return self.represent_scalar("tag:yaml.org,2002:null", "")


@dataclass(kw_only=True)
class MarkdownReview:
    yaml: ReviewYaml
    review_content: str | None = None


class ReviewYaml(TypedDict):
    date: datetime.date
    imdb_id: str
    title: str
    grade: str
    slug: str


def create_or_update(
    imdb_id: str,
    grade: str,
    full_title: str,
    date: datetime.date,
) -> MarkdownReview:
    markdown_review = next(
        (
            markdown_review
            for markdown_review in read_all()
            if markdown_review.yaml["imdb_id"] == imdb_id
        ),
        None,
    )

    if markdown_review:
        markdown_review.yaml["date"] = date
        markdown_review.yaml["grade"] = grade
        markdown_review.yaml["title"] = full_title
    else:
        markdown_review = MarkdownReview(
            yaml=ReviewYaml(
                imdb_id=imdb_id,
                title=full_title,
                slug=slugifier.slugify_title(full_title),
                grade=grade,
                date=date,
            )
        )

    _serialize(markdown_review)

    return markdown_review


def read_all() -> Iterable[MarkdownReview]:
    for file_path in glob(os.path.join(FOLDER_NAME, "*.md")):
        with open(file_path) as review_file:
            _, frontmatter, review_content = FM_REGEX.split(review_file.read(), 2)
            yield MarkdownReview(
                yaml=cast(ReviewYaml, yaml.safe_load(frontmatter)),
                review_content=review_content,
            )


def _generate_file_path(markdown_review: MarkdownReview) -> str:
    file_path = os.path.join(FOLDER_NAME, "{0}.md".format(markdown_review.yaml["slug"]))

    path_tools.ensure_file_path(file_path)

    return file_path


def _serialize(markdown_review: MarkdownReview) -> str:
    yaml.add_representer(type(None), _represent_none)

    file_path = _generate_file_path(markdown_review)

    stripped_content = str(markdown_review.review_content or "").strip()

    with open(file_path, "w") as output_file:
        output_file.write("---\n")
        yaml.dump(
            markdown_review.yaml,
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
