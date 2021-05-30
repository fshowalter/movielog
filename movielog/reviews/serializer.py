import os
import re
from datetime import date
from glob import glob
from typing import Any, Optional, Sequence, TypedDict, cast

import yaml
from slugify import slugify

from movielog.reviews.review import Review
from movielog.utils import path_tools
from movielog.utils.logging import logger

FOLDER_PATH = "reviews"

FM_REGEX = re.compile(r"^-{3,}\s*$", re.MULTILINE)


def represent_none(self: Any, _: Any) -> Any:
    return self.represent_scalar("tag:yaml.org,2002:null", "")


yaml.add_representer(type(None), represent_none)  # type: ignore


class ReviewYaml(TypedDict):
    sequence: int
    date: date
    imdb_id: str
    title: str
    grade: str
    slug: str
    venue: str
    venue_notes: Optional[str]


def deserialize(file_path: str) -> Review:
    with open(file_path, "r") as review_file:
        _, frontmatter, review_content = FM_REGEX.split(review_file.read(), 2)

    review_yaml = cast(ReviewYaml, yaml.safe_load(frontmatter))

    return Review(
        date=review_yaml["date"],
        grade=review_yaml["grade"],
        title=review_yaml["title"],
        imdb_id=review_yaml["imdb_id"],
        sequence=review_yaml["sequence"],
        slug=review_yaml["slug"],
        venue=review_yaml["venue"],
        venue_notes=review_yaml["venue_notes"],
        review_content=review_content,
    )


def deserialize_all() -> Sequence[Review]:
    reviews: list[Review] = []
    for review_file_path in glob(os.path.join(FOLDER_PATH, "*.md")):
        reviews.append(deserialize(review_file_path))

    reviews.sort(key=lambda review: review.sequence)

    return reviews


def generate_file_path(review: Review) -> str:
    file_name = slugify(
        "{0:04d} {1}".format(review.sequence, review.slug),
    )

    file_path = os.path.join(FOLDER_PATH, "{0}.md".format(file_name))

    path_tools.ensure_file_path(file_path)

    return file_path


def generate_yaml(review: Review) -> ReviewYaml:
    return ReviewYaml(
        sequence=review.sequence,
        date=review.date,
        imdb_id=review.imdb_id,
        title=review.title,
        grade=review.grade,
        slug=review.slug,
        venue=review.venue,
        venue_notes=review.venue_notes,
    )


def serialize(review: Review) -> str:
    file_path = generate_file_path(review)

    stripped_content = str(review.review_content or "").strip()

    with open(file_path, "w") as output_file:
        output_file.write("---\n")
        yaml.dump(
            generate_yaml(review),
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
