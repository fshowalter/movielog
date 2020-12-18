import json
import operator
import os
import re
from dataclasses import asdict, dataclass
from datetime import date
from glob import glob
from typing import Any, Dict, List, Optional, Sequence

import yaml
from slugify import slugify

from movielog import db, has_sequence, humanize
from movielog.logger import logger

SEQUENCE = "sequence"
FM_REGEX = re.compile(r"^-{3,}\s*$", re.MULTILINE)
REVIEWS = "reviews"
TABLE_NAME = REVIEWS
FOLDER_PATH = REVIEWS
IMDB_ID = "imdb_id"
TITLE = "title"
EMPTY_STRING = ""


def represent_none(self: Any, _: Any) -> Any:
    return self.represent_scalar("tag:yaml.org,2002:null", EMPTY_STRING)


yaml.add_representer(type(None), represent_none)  # type: ignore


@dataclass
class Review(object):
    sequence: Optional[int]
    imdb_id: str
    title: str
    date: date
    grade: str
    venue: str
    file_path: Optional[str]
    grade_value: Optional[int] = None
    slug: Optional[str] = None
    venue_notes: Optional[str] = None
    review_content: Optional[str] = None

    @classmethod
    def from_yaml_object(cls, file_path: str, yaml_object: Dict[str, Any]) -> "Review":
        grade = yaml_object["grade"]

        return Review(
            file_path=file_path,
            date=yaml_object["date"],
            grade=grade,
            grade_value=cls.grade_value_for_grade(grade),
            title=yaml_object["title"],
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

    @classmethod
    def load_all(cls) -> Sequence["Review"]:
        reviews: List[Review] = []
        for review_file_path in glob(os.path.join(FOLDER_PATH, "*.md")):
            reviews.append(Review.from_file_path(review_file_path))

        reviews.sort(key=operator.attrgetter(SEQUENCE))

        logger.log("Read {} {}.", humanize.intcomma(len(reviews)), "reviews")
        return reviews

    @classmethod
    def from_file_path(cls, file_path: str) -> "Review":
        with open(file_path, "r") as review_file:
            _, fm, review_content = FM_REGEX.split(review_file.read(), 2)

        review = cls.from_yaml_object(file_path, yaml.safe_load(fm))
        review.file_path = file_path
        review.review_content = review_content

        return review

    def ensure_file_path(self) -> str:
        file_path = self.file_path

        if not file_path:
            file_name = slugify(
                f"{self.sequence:04} {self.title}", replacements=[("'", EMPTY_STRING)]
            )
            file_path = os.path.join(FOLDER_PATH, "{0}.md".format(file_name))

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        return file_path

    def as_yaml(self) -> Dict[str, Any]:
        return {
            SEQUENCE: self.sequence,
            "date": self.date,
            IMDB_ID: self.imdb_id,
            TITLE: self.title,
            "grade": self.grade,
            "slug": slugify(self.title, replacements=[("'", EMPTY_STRING)]),
            "venue": self.venue,
            "venue_notes": self.venue_notes,
        }

    def save(self) -> str:
        if not self.sequence:
            self.sequence = has_sequence.next_sequence(type(self).load_all())

        file_path = self.ensure_file_path()

        stripped_content = str(self.review_content or "").strip()

        with open(file_path, "w") as output_file:
            output_file.write("---\n")
            yaml.dump(
                self.as_yaml(),
                encoding="utf-8",
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
                stream=output_file,
            )
            output_file.write("---\n\n")
            output_file.write(stripped_content)

        self.file_path = file_path

        logger.log("Wrote {}", self.file_path)

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
        title="{0} ({1})".format(title, year),
        date=review_date,
        grade=grade,
        venue=venue,
        venue_notes=venue_notes,
        sequence=0,
        file_path=None,
    )

    review.save()

    return review


def existing_review(imdb_id: str) -> Optional[Review]:
    reviews = sorted(
        Review.load_all(), key=lambda review: review.sequence or 0, reverse=True
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
            , runtime_minutes
            FROM reviews
            INNER JOIN movies ON reviews.movie_imdb_id = movies.imdb_id
            INNER JOIN release_dates ON reviews.movie_imdb_id = release_dates.movie_imdb_id
            INNER JOIN sort_titles ON reviews.movie_imdb_id = sort_titles.movie_imdb_id
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
    def fetch_countries_for_title_id(cls, title_imdb_id: str) -> List[str]:
        rows = db.exec_query(
            """
                SELECT
                country
                FROM countries
                WHERE movie_imdb_id = "{0}";
                """.format(
                title_imdb_id
            )
        )

        return [row["country"] for row in rows]

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

        reviews = Review.load_all()
        ReviewsTable.recreate()
        ReviewsTable.insert_reviews(reviews)

        review_rows = cls.fetch_reviews()

        for review_row in review_rows:
            review_row["directors"] = cls.fetch_directors_for_title_id(
                title_imdb_id=review_row[IMDB_ID]
            )

            review_row["aka_titles"] = cls.fetch_aka_titles_for_title_id(
                title_imdb_id=review_row[IMDB_ID],
                title=review_row[TITLE],
                original_title=review_row["original_title"],
            )

            review_row["principal_cast"] = cls.fetch_principal_cast(
                principal_cast_ids_with_commas=review_row["principal_cast_ids"]
            )
            review_row["countries"] = cls.fetch_countries_for_title_id(
                title_imdb_id=review_row[IMDB_ID]
            )

        file_path = os.path.join("export", "reviewed_movies.json")

        with open(file_path, "w") as output_file:
            output_file.write(json.dumps([dict(row) for row in review_rows]))
