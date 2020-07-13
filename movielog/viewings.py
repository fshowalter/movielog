import json
import operator
import os
from dataclasses import asdict, dataclass
from datetime import date
from glob import glob
from typing import Any, Dict, List, Optional, Sequence, Set

from slugify import slugify

from movielog import db, humanize, performing_credits, yaml_file
from movielog.logger import logger

TABLE_NAME = "viewings"
SEQUENCE = "sequence"


@dataclass
class Viewing(yaml_file.Movie, yaml_file.WithSequence):
    venue: str
    date: date
    sort_title: Optional[str] = None

    @classmethod
    def load_all(cls) -> Sequence["Viewing"]:
        viewings: List[Viewing] = []
        for yaml_file_path in glob(os.path.join(TABLE_NAME, "*.yml")):
            viewings.append(cls.from_file_path(yaml_file_path))

        viewings.sort(key=operator.attrgetter(SEQUENCE))

        logger.log("Loaded {} {}.", humanize.intcomma(len(viewings)), TABLE_NAME)
        return viewings

    @classmethod
    def build_sort_title(cls, title: str) -> str:
        title_lower = title.lower()
        title_words = title.split(" ")
        lower_words = title_lower.split(" ")
        articles = set(["a", "an", "the"])

        if (len(title_words) > 1) and (lower_words[0] in articles):
            return "{0}, {1}".format(
                " ".join(title_words[1 : len(title_words)]), title_words[0]
            )

        return title

    @classmethod
    def from_yaml_object(cls, file_path: str, yaml_object: Dict[str, Any]) -> "Viewing":
        title, year = cls.split_title_and_year(yaml_object["title"])
        sort_title = cls.build_sort_title(title)

        return cls(
            imdb_id=yaml_object["imdb_id"],
            title=title,
            year=year,
            venue=yaml_object["venue"],
            sequence=yaml_object[SEQUENCE],
            date=yaml_object["date"],
            file_path=file_path,
            sort_title=sort_title,
        )

    def generate_slug(self) -> str:
        slug = slugify(f"{self.sequence:04} {self.title_with_year}")
        return str(slug)

    @classmethod
    def folder_path(cls) -> str:
        return TABLE_NAME

    def as_yaml(self) -> Dict[str, Any]:
        return {
            SEQUENCE: self.sequence,
            "date": self.date,
            "imdb_id": self.imdb_id,
            "title": self.title_with_year,
            "venue": self.venue,
        }


class ViewingsTable(db.Table):
    table_name = TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "movie_imdb_id" TEXT NOT NULL REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "date" DATE NOT NULL,
            "sequence" INT NOT NULL,
            "venue" TEXT NOT NULL,
            "sort_title" TEXT NOT NULL);
        """

    @classmethod
    def insert_viewings(cls, viewings: Sequence[Viewing]) -> None:
        ddl = """
          INSERT INTO {0}(movie_imdb_id, date, sequence, venue, sort_title)
          VALUES(:imdb_id, :date, :sequence, :venue, :sort_title);
        """.format(
            cls.table_name
        )

        parameter_seq = [asdict(viewing) for viewing in viewings]

        cls.insert(ddl=ddl, parameter_seq=parameter_seq)
        cls.add_index(SEQUENCE)
        cls.add_index("venue")
        cls.add_index("movie_imdb_id")
        cls.validate(viewings)


def update() -> None:
    logger.log("==== Begin updating {}...", TABLE_NAME)

    viewings = Viewing.load_all()

    ViewingsTable.recreate()
    ViewingsTable.insert_viewings(viewings)

    performing_credits.update(imdb_ids())


def export() -> None:
    logger.log("==== Begin exporting {}...", TABLE_NAME)

    query = """
        SELECT imdb_id, title, year, date, sequence, venue, original_title, runtime_minutes, sort_title
        FROM viewings INNER JOIN movies ON movie_imdb_id = imdb_id;
        """

    with db.connect() as connection:
        rows = connection.execute(query).fetchall()

    file_path = os.path.join("export", "viewings.json")

    with open(file_path, "w") as output_file:
        output_file.write(json.dumps([dict(row) for row in rows]))


def add(imdb_id: str, title: str, venue: str, viewing_date: date, year: int) -> Viewing:
    viewing = Viewing(
        imdb_id=imdb_id,
        title=title,
        venue=venue,
        date=viewing_date,
        year=year,
        file_path=None,
        sequence=None,
    )

    viewing.save()
    update()

    return viewing


def venues() -> Sequence[str]:
    venue_items = list(
        dict.fromkeys([viewing.venue for viewing in Viewing.load_all()]).keys()
    )
    venue_items.sort()
    return venue_items


def imdb_ids() -> Set[str]:
    return set([viewing.imdb_id for viewing in Viewing.load_all()])
