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
    imdb_id: str
    date: date
    grade: str
    venue: str
    grade_value: Optional[int] = None
    slug: Optional[str] = None
    venue_notes: Optional[str] = None
    review_content: Optional[str] = None

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
            venue=yaml_object["venue"],
            venue_notes=yaml_object["venue_notes"],
        )

    @classmethod
    def grade_value_for_grade(cls, grade: str) -> Optional[int]:
        if not grade:
            return None

        grade_map = {
            "A": 5,
            "B": 4,
            "C": 3,
            "D": 3,
            "F": 1,
        }

        base_grade = grade_map.get(grade[0], 3)

        if grade[-1]

    def generate_slug(self) -> str:
        return str(slugify(self.title_with_year))

    def generate_filename(self) -> str:
        slug = slugify(f"{self.sequence:04} {self.title_with_year}")
        return str(slug)

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
            "venue": self.venue,
            "venue_notes": self.venue_notes,
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
            "grade" TEXT NOT NULL,
            "grade_value" INT NOT NULL,
            "slug" TEXT NOT NULL,
            "venue" TEXT NOT NULL);
        DROP TRIGGER IF EXISTS multiple_slugs;
        CREATE TRIGGER multiple_slugs
            BEFORE INSERT ON "{0}"
            BEGIN
                SELECT RAISE(FAIL, "conflicting slugs")
                FROM "{0}"
                WHERE movie_imdb_id = NEW.movie_imdb_id
                AND slug != NEW.slug;
            END;
        """

    @classmethod
    def insert_reviews(cls, reviews: Sequence[Review]) -> None:
        ddl = """
          INSERT INTO {0}(movie_imdb_id, date, sequence, grade, grade_value, slug, venue)
          VALUES(:imdb_id, :date, :sequence, :grade, :grade_value, :slug, :venue);
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


def add(
    imdb_id: str,
    title: str,
    review_date: date,
    year: int,
    grade: str,
    venue: str,
    venue_notes: Optional[str] = None,
) -> Review:
    review = Review(
        imdb_id=imdb_id,
        title=title,
        date=review_date,
        year=year,
        grade=grade,
        venue=venue,
        venue_notes=venue_notes,
        sequence=None,
        file_path=None,
    )

    review.save()
    update()

    return review


def existing_review(imdb_id: str) -> Optional[Review]:
    reviews = sorted(
        Review.load_all(), key=lambda review: review.sequence, reverse=True
    )

    return next((review for review in reviews if review.imdb_id is imdb_id), None)


def export() -> None:
    logger.log("==== Begin exporting {}...", TABLE_NAME)

    query = """
        SELECT
          DISTINCT(reviews.movie_imdb_id) AS imdb_id
        , title
        , year
        , reviews.date
        , reviews.sequence
        , grade
        , grade_value
        , slug
        , sort_title
        , principal_cast_ids
        FROM reviews
        INNER JOIN movies ON reviews.movie_imdb_id = movies.imdb_id
        INNER JOIN viewings ON viewings.movie_imdb_id = movies.imdb_id;
        """

    with db.connect() as connection:
        review_rows = connection.execute(query).fetchall()

    reviews = []

    for review_row in review_rows:
        review = dict(review_row)

        review["directors"] = []

        directors_query = """
            SELECT
            full_name
            FROM people
            INNER JOIN directing_credits ON person_imdb_id = imdb_id
            WHERE movie_imdb_id = "{0}";
            """.format(
            review["imdb_id"]
        )

        with db.connect() as connection:
            director_rows = connection.execute(directors_query).fetchall()

        for director_row in director_rows:
            review["directors"].append(dict(director_row))

        review["principal_cast"] = []

        principal_cast_ids = review["principal_cast_ids"].split(",")

        for principal_cast_id in principal_cast_ids:
            principal_cast_query = """
            SELECT
            full_name
            FROM people
            WHERE imdb_id = "{0}";
            """.format(
                principal_cast_id
            )

            with db.connect() as connection:
                cast_rows = connection.execute(principal_cast_query).fetchall()

            for cast_row in cast_rows:
                review["principal_cast"].append(dict(cast_row))

        reviews.append(review)

    file_path = os.path.join("export", "reviews.json")

    with open(file_path, "w") as output_file:
        output_file.write(json.dumps([dict(row) for row in reviews]))
