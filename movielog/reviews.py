import operator
import os
import re
from dataclasses import dataclass
from datetime import date
from glob import glob
from typing import Any, List, Optional, Sequence, Tuple

import yaml
from slugify import slugify

from movielog.internal import humanize
from movielog.logger import logger

TITLE_AND_YEAR_REGEX = re.compile(r"^(.*)\s\((\d{4})\)$")
SEQUENCE = "sequence"
FM_REGEX = re.compile(r"^-{3,}\s*$", re.MULTILINE)


class ReviewError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


@dataclass
class Review(object):
    imdb_id: str
    title: str
    sequence: int
    date: date
    year: int
    file_path: Optional[str]
    grade: Optional[str] = None
    review_content: Optional[str] = None

    @classmethod
    def load(cls, file_path: str) -> "Review":
        _, fm, review_content = cls.read_review_file(file_path)

        front_matter = yaml.safe_load(fm)
        title, year = cls.split_title_and_year(front_matter["title"])

        return cls(
            imdb_id=front_matter["imdb_id"],
            title=title,
            year=year,
            review_content=review_content,
            sequence=front_matter[SEQUENCE],
            date=front_matter["date"],
            file_path=file_path,
        )

    @property
    def title_with_year(self) -> str:
        return f"{self.title} ({self.year})"

    @property
    def slug(self) -> str:
        return str(slugify(self.title_with_year))

    @classmethod
    def read_review_file(cls, file_path: str) -> List[str]:
        with open(file_path, "r") as review_file:
            review_content = review_file.read()

        return FM_REGEX.split(review_content, 2)

    @classmethod
    def split_title_and_year(cls, title_and_year: str) -> Tuple[str, int]:
        match = TITLE_AND_YEAR_REGEX.match(title_and_year)
        if match:
            return (match.group(1), int(match.group(2)))
        raise ReviewError(f"Unable to parse {title_and_year} for title and year")

    def save(self) -> str:
        file_path = self.file_path

        if not file_path:
            slug = slugify(self.title_with_year)
            file_path = os.path.join("reviews", f"{slug}.md")
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

        with open(file_path, "w", encoding="utf-8") as output_file:
            output_file.write(self.to_string())

        self.file_path = file_path

        logger.log("Wrote {}", self.file_path)

        return file_path

    def to_string(self) -> Any:
        front_matter = yaml.dump(
            {
                SEQUENCE: self.sequence,
                "date": self.date,
                "imdb_id": self.imdb_id,
                "title": self.title_with_year,
                "grade": self.grade,
                "slug": self.slug,
            },
            encoding="utf-8",
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
        stripped_content = str(self.review_content).strip()
        return f'---\n{front_matter.decode("utf-8")}---\n\n{stripped_content}'


def add(imdb_id: str, title: str, review_date: date, year: int) -> Review:
    existing_reviews = _load_reviews()
    next_sequence = len(existing_reviews) + 1

    if existing_reviews:
        last_review = existing_reviews[-1]

        if last_review.sequence != (next_sequence - 1):
            raise ReviewError(
                "Last review ({0} has sequence {1} but next sequence is {2}".format(
                    existing_reviews[-1:], last_review.sequence, next_sequence,
                ),
            )

    review = Review(
        imdb_id=imdb_id,
        title=title,
        date=review_date,
        year=year,
        sequence=next_sequence,
        file_path=None,
    )

    review.save()

    return review


def _load_reviews() -> Sequence[Review]:
    reviews: List[Review] = []
    for review_file_path in glob(os.path.join("reviews", "*.md")):
        reviews.append(Review.load(review_file_path))

    reviews.sort(key=operator.attrgetter(SEQUENCE))

    logger.log("Loaded {} {}.", humanize.intcomma(len(reviews)), "reviews")
    return reviews
