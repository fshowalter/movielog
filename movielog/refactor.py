from __future__ import annotations

import datetime
import json
import os
import re
from dataclasses import asdict, dataclass
from glob import glob
from typing import Any, Optional, Sequence, TypedDict, cast

import yaml
from slugify import slugify

from movielog.utils import path_tools
from movielog.utils.logging import logger

FM_REGEX = re.compile(r"^-{3,}\s*$", re.MULTILINE)


def represent_none(self: Any, _: Any) -> Any:
    return self.represent_scalar("tag:yaml.org,2002:null", "")


yaml.add_representer(type(None), represent_none)


class ReviewYaml(TypedDict):
    sequence: int
    date: datetime.date
    imdb_id: str
    title: str
    grade: str
    slug: str
    venue: str
    venue_notes: Optional[str]


class NewReviewYaml(TypedDict):
    date: datetime.date
    imdb_id: str
    title: str
    grade: str
    slug: str


@dataclass
class NewReview(object):
    imdb_id: str
    title: str
    date: datetime.date
    grade: str
    slug: str
    review_content: Optional[str] = None


@dataclass
class Review(object):
    sequence: int
    imdb_id: str
    title: str
    date: datetime.date
    grade: str
    venue: str
    slug: str
    venue_notes: Optional[str] = None
    review_content: Optional[str] = None

    @property
    def grade_value(self) -> float:
        value_modifier = 0.33

        grade_map = {
            "A": 5.0,
            "B": 4.0,
            "C": 3.0,
            "D": 2.0,
            "F": 1.0,
        }

        grade_value = grade_map.get(self.grade[0], 3)
        modifier = self.grade[-1]

        if modifier == "+":
            grade_value += value_modifier

        if modifier == "-":
            grade_value -= value_modifier

        return grade_value


def deserialize_review(file_path: str) -> Review:
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


def deserialize_all_reviews() -> Sequence[Review]:
    reviews: list[Review] = []
    for review_file_path in glob(os.path.join("reviews", "*.md")):
        reviews.append(deserialize_review(review_file_path))

    reviews.sort(key=lambda review: review.sequence)

    return reviews


@dataclass
class Viewing(object):
    sequence: int
    date: datetime.date
    imdb_id: str
    title: str
    venue: str


class JsonViewing(TypedDict):
    sequence: int
    date: str
    imdb_id: str
    title: str
    venue: str


@dataclass
class NewJsonViewing(object):
    sequence: int
    date: datetime.date
    imdb_id: str
    slug: str
    venue: Optional[str]
    medium: Optional[str]
    medium_notes: Optional[str]


def deserialize_viewing(file_path: str) -> Viewing:
    json_object = None

    with open(file_path, "r") as json_file:
        json_object = cast(JsonViewing, json.load(json_file))

    return Viewing(
        imdb_id=json_object["imdb_id"],
        title=json_object["title"],
        venue=json_object["venue"],
        sequence=json_object["sequence"],
        date=datetime.date.fromisoformat(json_object["date"]),
    )


def deserialize_all_viewings() -> Sequence[Viewing]:
    file_paths = glob(os.path.join("viewings", "*.json"))

    return [deserialize_viewing(file_path) for file_path in sorted(file_paths)]


def venue_for_review(review: Review) -> Optional[str]:
    if review.venue in ("Prince Charles Cinema"):
        return review.venue

    return None


def medium_for_review(review: Review) -> str:
    if review.venue in ("Prince Charles Cinema"):
        return "35mm"

    return review.venue


def venue_for_viewing(viewing: Viewing) -> Optional[str]:
    if viewing.venue in {
        "AFI Silver",
        "Alamo Drafthouse Cinema - One Loudoun",
        "Alamo Drafthouse Cinema - Winchester",
        "Alamo Drafthouse Cinema - Woodbridge",
        "Alamo On Demand",
        "AMC Tysons Corner 16",
        "Angelika Film Center Mosaic",
        "Landmark E Street Cinema",
        "Prince Charles Cinema",
        "Sun &amp; Surf Cinema",
        "The Black Cat",
    }:
        return viewing.venue

    return None


def medium_for_viewing(viewing: Viewing) -> Optional[str]:
    if viewing.venue in {
        "4k UHD Blu-ray",
        "Alamo On Demand",
        "Amazon",
        "archive.org",
        "Arrow Player",
        "Arte",
        "Blu-ray",
        "Criterion Channel",
        "Disney+",
        "DVD",
        "Encore HD",
        "FandangoNOW",
        "FXM",
        "HBO GO",
        "HBO HD",
        "HBO Max",
        "HDNet",
        "Hoopla",
        "Hulu",
        "iTunes",
        "Kanopy",
        "Netflix",
        "OK.ru",
        "Shudder",
        "TCM",
        "TCM HD",
        "VHS-rip",
        "Vudu",
        "Watch TCM",
        "YouTube",
    }:
        return viewing.venue

    return None


def generate_viewing_file_path(viewing: NewJsonViewing) -> str:
    file_name = slugify(
        "{0:04d} {1}".format(viewing.sequence, viewing.slug),
    )

    file_path = os.path.join("viewings_test", "{0}.json".format(file_name))

    path_tools.ensure_file_path(file_path)

    return file_path


def generate_review_file_path(review: NewReview) -> str:
    file_path = os.path.join("reviews_test", "{0}.md".format(review.slug))

    path_tools.ensure_file_path(file_path)

    return file_path


def serialize_viewing(viewing: NewJsonViewing) -> str:
    file_path = generate_viewing_file_path(viewing)

    with open(file_path, "w") as output_file:
        json.dump(asdict(viewing), output_file, indent=4, default=str)

    return file_path


def generate_new_review_yaml(review: NewReview) -> NewReviewYaml:
    return NewReviewYaml(
        date=review.date,
        imdb_id=review.imdb_id,
        title=review.title,
        grade=review.grade,
        slug=review.slug,
    )


def serialize_review(review: NewReview) -> str:
    file_path = generate_review_file_path(review)

    stripped_content = str(review.review_content or "").strip()

    with open(file_path, "w") as output_file:
        output_file.write("---\n")
        yaml.dump(
            generate_new_review_yaml(review),
            encoding="utf-8",
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            stream=output_file,
        )
        output_file.write("---\n\n")
        output_file.write(stripped_content)

    return file_path


if __name__ == "__main__":
    reviews = deserialize_all_reviews()
    viewings = deserialize_all_viewings()

    for review in reviews:

        new_viewing = NewJsonViewing(
            sequence=review.sequence,
            date=review.date,
            imdb_id=review.imdb_id,
            slug=review.slug,
            venue=venue_for_review(review),
            medium=medium_for_review(review),
            medium_notes=review.venue_notes,
        )

        serialize_viewing(new_viewing)

        new_review = NewReview(
            date=review.date,
            imdb_id=review.imdb_id,
            title=review.title,
            grade=review.grade,
            review_content=review.review_content,
            slug=review.slug,
        )

        if os.path.exists(generate_review_file_path(new_review)):
            logger.log("Duplicate review: {0}-{1}", review.sequence, review.slug)
        else:
            serialize_review(new_review)

    for viewing in viewings:
        viewing_slug = slugify(viewing.title, replacements=[("'", "")])

        new_viewing = NewJsonViewing(
            sequence=viewing.sequence,
            date=viewing.date,
            imdb_id=viewing.imdb_id,
            slug=viewing_slug,
            venue=venue_for_viewing(viewing),
            medium=medium_for_viewing(viewing),
            medium_notes=None,
        )

        serialize_viewing(new_viewing)
