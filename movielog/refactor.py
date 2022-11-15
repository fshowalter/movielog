from __future__ import annotations

import datetime
import json
import os
import re
from dataclasses import dataclass
from glob import glob
from typing import Any, Optional, Sequence, TypedDict, cast

import yaml

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
    date: str
    imdb_id: str
    title: str
    venue: str
    source: str
    source_notes: str
    viewing_notes: str


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


if __name__ == "__main__":
    reviews = deserialize_all_reviews()
    viewings = deserialize_all_viewings()
