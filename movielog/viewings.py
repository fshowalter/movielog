import json
import operator
import os
from dataclasses import asdict, dataclass
from datetime import date
from glob import glob
from typing import Any, Dict, List, Optional, Sequence

from slugify import slugify

from movielog import db, has_sequence, humanize
from movielog.logger import logger

TABLE_NAME = "viewings"
FOLDER_PATH = "viewings"
SEQUENCE = "sequence"
BLANK_SPACE = " "


@dataclass
class Viewing(object):
    file_path: Optional[str]
    imdb_id: str
    title: str
    venue: str
    date: date
    sequence: Optional[int]

    @classmethod
    def from_file_path(cls, file_path: str) -> "Viewing":
        json_object = None

        with open(file_path, "r") as json_file:
            json_object = json.load(json_file)

        instance = cls.from_json_object(file_path=file_path, json_object=json_object)
        instance.file_path = file_path

        return instance

    @classmethod
    def load_all(cls) -> Sequence["Viewing"]:
        logger.log("==== Begin reading {} from disk...", TABLE_NAME)

        viewings: List[Viewing] = []
        for yaml_file_path in glob(os.path.join(FOLDER_PATH, "*.json")):
            viewings.append(cls.from_file_path(yaml_file_path))

        viewings.sort(key=operator.attrgetter(SEQUENCE))

        logger.log("Read {} {}.", humanize.intcomma(len(viewings)), TABLE_NAME)
        return viewings

    @classmethod
    def from_json_object(cls, file_path: str, json_object: Dict[str, Any]) -> "Viewing":
        return cls(
            imdb_id=json_object["imdb_id"],
            title=json_object["title"],
            venue=json_object["venue"],
            sequence=json_object[SEQUENCE],
            date=json_object["date"],
            file_path=file_path,
        )

    def ensure_file_path(self) -> str:
        file_path = self.file_path

        if not file_path:
            file_name = f"{self.sequence:04} {self.title}"
            slug = slugify(file_name, replacements=[("'", "")])
            file_path = os.path.join(FOLDER_PATH, "{0}.json".format(slug))

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        return file_path

    def as_dict(self) -> Dict[str, Any]:
        viewing_dict = asdict(self)
        viewing_dict.pop("file_path", None)
        return viewing_dict

    def save(self) -> str:
        if not self.sequence:
            self.sequence = has_sequence.next_sequence(type(self).load_all())

        file_path = self.ensure_file_path()

        with open(file_path, "w") as output_file:
            output_file.write(json.dumps(self.as_dict(), default=str, indent=2))

        self.file_path = file_path

        logger.log("Wrote {}", self.file_path)

        return file_path


class ViewingsTable(db.Table):
    table_name = TABLE_NAME

    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "movie_imdb_id" TEXT NOT NULL REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "date" DATE NOT NULL,
            "sequence" INT NOT NULL,
            "venue" TEXT NOT NULL);
        """

    @classmethod
    def insert_viewings(cls, viewings: Sequence[Viewing]) -> None:
        ddl = """
          INSERT INTO {0}(movie_imdb_id, date, sequence, venue)
          VALUES(:imdb_id, :date, :sequence, :venue);
        """.format(
            cls.table_name
        )

        parameter_seq = [asdict(viewing) for viewing in viewings]

        cls.insert(ddl=ddl, parameter_seq=parameter_seq)
        cls.add_index(SEQUENCE)
        cls.add_index("venue")
        cls.add_index("movie_imdb_id")
        cls.validate(viewings)


def export(viewings: Sequence[Viewing]) -> None:
    logger.log("==== Begin exporting {}...", TABLE_NAME)

    ViewingsTable.recreate()
    ViewingsTable.insert_viewings(viewings)

    query = """
        SELECT
            imdb_id
        , title
        , year
        , release_date
        , date as viewing_date
        , strftime('%Y', date) as viewing_year
        , sequence
        , venue
        , original_title
        , sort_title
        FROM viewings
        INNER JOIN movies ON viewings.movie_imdb_id = imdb_id
        INNER JOIN release_dates ON release_dates.movie_imdb_id = viewings.movie_imdb_id
        INNER JOIN sort_titles on sort_titles.movie_imdb_id = viewings.movie_imdb_id;
        """

    with db.connect() as connection:
        rows = connection.execute(query).fetchall()

    file_path = os.path.join("export", "viewings.json")

    with open(file_path, "w") as output_file:
        output_file.write(json.dumps([dict(row) for row in rows]))


def add(imdb_id: str, title: str, venue: str, viewing_date: date, year: int) -> Viewing:
    viewing = Viewing(
        imdb_id=imdb_id,
        title="{0} ({1})".format(title, year),
        venue=venue,
        date=viewing_date,
        file_path=None,
        sequence=0,
    )

    viewing.save()

    return viewing


def load_all() -> Sequence[Viewing]:
    return Viewing.load_all()


def venues() -> Sequence[str]:
    venue_items = list(
        dict.fromkeys([viewing.venue for viewing in Viewing.load_all()]).keys()
    )
    venue_items.sort()
    return venue_items
