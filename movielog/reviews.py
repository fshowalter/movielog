import json
import operator
import os
import re
from dataclasses import asdict, dataclass
from datetime import date
from glob import glob
from typing import Any, Callable, Dict, List, Optional, Sequence

import yaml
from slugify import slugify

from movielog import db, humanize, yaml_file
from movielog.logger import logger

SEQUENCE = "sequence"
FM_REGEX = re.compile(r"^-{3,}\s*$", re.MULTILINE)
REVIEWS = "reviews"
TABLE_NAME = REVIEWS


@dataclass  # noqa: WPS214
class Review(yaml_file.Movie, yaml_file.WithSequence):
    date: date
    grade: Optional[str] = None
    grade_value: Optional[int] = None
    review_content: Optional[str] = None
    slug: Optional[str] = None

    @classmethod
    def from_yaml_object(cls, file_path: str, yaml_object: Dict[str, Any]) -> "Review":
        title, year = cls.split_title_and_year(yaml_object["title"])

        return Review(
            file_path=file_path,
            date=yaml_object["date"],
            grade=yaml_object["grade"],
            grade_value=cls.grade_value_for_grade(yaml_object["grade"]),
            title=title,
            year=year,
            imdb_id=yaml_object["imdb_id"],
            sequence=yaml_object["sequence"],
            slug=yaml_object["slug"],
        )

    @classmethod
    def grade_value_for_grade(cls, grade: str) -> int:
        grade_map = {
            "A": 5,
            "B": 4,
            "C": 3,
            "D": 2,
            "F": 1,
        }

        return grade_map.get(grade[0], 3)

    def generate_slug(self) -> str:
        return str(slugify(self.title_with_year))

    @classmethod
    def folder_path(cls) -> str:
        return REVIEWS

    @classmethod
    def extension(cls) -> str:
        return "md"

    def as_yaml(self) -> Dict[str, Any]:
        return {
            SEQUENCE: self.sequence,
            "date": self.date,
            "imdb_id": self.imdb_id,
            "title": self.title_with_year,
            "grade": self.grade,
            "slug": self.generate_slug(),
        }

    @classmethod
    def load_all(cls) -> Sequence["Review"]:
        reviews: List[Review] = []
        for review_file_path in glob(os.path.join(cls.folder_path(), "*.md")):
            reviews.append(Review.from_file_path(review_file_path))

        reviews.sort(key=operator.attrgetter(SEQUENCE))

        logger.log("Loaded {} {}.", humanize.intcomma(len(reviews)), "reviews")
        return reviews

    @classmethod
    def from_file_path(cls, file_path: str) -> "Review":
        with open(file_path, "r") as review_file:
            _, fm, review_content = FM_REGEX.split(review_file.read(), 2)

        review = cls.from_yaml_object(file_path, yaml.safe_load(fm))
        review.file_path = file_path
        review.review_content = review_content

        return review

    def save(self, log_function: Optional[Callable[[], None]] = None) -> str:
        file_path = super().save(log_function=log_function)

        stripped_content = str(self.review_content or "").strip()

        with open(file_path, "r") as original_file:
            original_content = original_file.read()

        with open(file_path, "wb") as new_file:
            new_file.write(
                f"---\n{original_content}---\n\n{stripped_content}".encode("utf-8")
            )

        return file_path


class ReviewsTable(db.Table):
    table_name = TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "movie_imdb_id" TEXT NOT NULL REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "date" DATE NOT NULL,
            "sequence" INT NOT NULL,
            "grade_value" INT NOT NULL);
        """

    @classmethod
    def insert_reviews(cls, reviews: Sequence[Review]) -> None:
        ddl = """
          INSERT INTO {0}(movie_imdb_id, date, sequence, grade_value)
          VALUES(:imdb_id, :date, :sequence, :grade_value);
        """.format(
            cls.table_name
        )

        parameter_seq = [asdict(review) for review in reviews]

        cls.insert(ddl=ddl, parameter_seq=parameter_seq)
        cls.add_index(SEQUENCE)
        cls.add_index("movie_imdb_id")
        cls.validate(reviews)


def update() -> None:
    logger.log("==== Begin updating {}...", TABLE_NAME)

    reviews = Review.load_all()

    ReviewsTable.recreate()
    ReviewsTable.insert_reviews(reviews)


def add(imdb_id: str, title: str, review_date: date, year: int) -> Review:
    review = Review(
        imdb_id=imdb_id,
        title=title,
        date=review_date,
        year=year,
        sequence=None,
        file_path=None,
    )

    review.save()
    update()

    return review


def export() -> None:
    logger.log("==== Begin exporting {}...", REVIEWS)

    reviews = Review.load_all()

    file_path = os.path.join("export", "reviews.json")

    with open(file_path, "w") as output_file:
        output_file.write(
            json.dumps([asdict(review) for review in reviews], default=str)
        )
