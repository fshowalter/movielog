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
IMDB_ID = "imdb_id"
TITLE = "title"


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
        title, year = cls.split_title_and_year(yaml_object[TITLE])

        return Review(
            file_path=file_path,
            date=yaml_object["date"],
            grade=yaml_object["grade"],
            grade_value=cls.grade_value_for_grade(yaml_object["grade"]),
            title=title,
            year=year,
            imdb_id=yaml_object[IMDB_ID],
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
            "A": 12,
            "B": 9,
            "C": 6,
            "D": 3,
            "F": 1,
        }

        grade_value = grade_map.get(grade[0], 3)
        modifier = grade[-1]

        if modifier == "+":
            grade_value = grade_value + 1

        if modifier == "-":
            grade_value = grade_value - 1

        return grade_value

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
            IMDB_ID: self.imdb_id,
            TITLE: self.title_with_year,
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
        sequence=0,
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
    Exporter.export()


class Exporter(object):
    @classmethod
    def fetch_reviews(cls) -> List[Dict[str, Any]]:
        reviews = []

        rows = db.exec_query(
            """
            SELECT
            DISTINCT(reviews.movie_imdb_id) AS imdb_id
            , title
            , original_title
            , year
            , reviews.date
            , reviews.sequence
            , release_date
            , grade as last_review_grade
            , grade_value as last_review_grade_value
            , slug
            , sort_title
            , principal_cast_ids
            FROM reviews
            INNER JOIN movies ON reviews.movie_imdb_id = movies.imdb_id
            INNER JOIN release_dates ON reviews.movie_imdb_id = release_dates.movie_imdb_id
            INNER JOIN viewings ON viewings.movie_imdb_id = movies.imdb_id
            ORDER BY sort_title ASC;
            """
        )  # noqa: WPS355

        for row in rows:
            reviews.append(dict(row))

        return reviews

    @classmethod
    def fetch_directors_for_title_id(cls, title_imdb_id: str) -> List[Dict[str, Any]]:
        rows = db.exec_query(
            """
                SELECT
                full_name
                FROM people
                INNER JOIN directing_credits ON person_imdb_id = imdb_id
                WHERE movie_imdb_id = "{0}";
                """.format(
                title_imdb_id
            )
        )

        directors = []

        for row in rows:
            directors.append(dict(row))

        return directors

    @classmethod
    def fetch_aka_titles_for_title_id(
        cls, title_imdb_id: str, title: str, original_title: str
    ) -> List[Dict[str, Any]]:
        rows = db.exec_query(
            """
                SELECT
                title
                FROM aka_titles
                WHERE region = "US"
                AND movie_imdb_id = "{0}"
                AND title != "{1}"
                AND (attributes IS NULL
                    OR (attributes NOT LIKE "%working title%"
                    AND attributes NOT LIKE "%alternative spelling%"));
                """.format(  # noqa: WPS323
                title_imdb_id, title
            )
        )

        aka_titles = []

        for row in rows:
            aka_titles.append(row[TITLE])

        if original_title != title:
            if original_title not in aka_titles:
                aka_titles.append(original_title)

        return aka_titles

    @classmethod
    def fetch_principal_cast(
        cls, principal_cast_ids_with_commas: str
    ) -> List[Dict[str, Any]]:
        principal_cast = []

        principal_cast_ids = principal_cast_ids_with_commas.split(",")

        for principal_cast_id in principal_cast_ids:
            rows = db.exec_query(
                """
                SELECT
                full_name
                FROM people
                WHERE imdb_id = "{0}";
                """.format(
                    principal_cast_id
                )
            )

            for row in rows:
                principal_cast.append(dict(row))

        return principal_cast

    @classmethod
    def export(cls) -> None:
        logger.log("==== Begin exporting {}...", "reviewed movies")

        reviews = cls.fetch_reviews()

        for review in reviews:
            review["directors"] = cls.fetch_directors_for_title_id(
                title_imdb_id=review[IMDB_ID]
            )

            review["aka_titles"] = cls.fetch_aka_titles_for_title_id(
                title_imdb_id=review[IMDB_ID],
                title=review[TITLE],
                original_title=review["original_title"],
            )

            review["principal_cast"] = cls.fetch_principal_cast(
                principal_cast_ids_with_commas=review["principal_cast_ids"]
            )

        file_path = os.path.join("export", "reviewed_movies.json")

        with open(file_path, "w") as output_file:
            output_file.write(json.dumps([dict(row) for row in reviews]))
