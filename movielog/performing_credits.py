import os
from dataclasses import asdict, dataclass
from typing import Any, List, Optional, Sequence

import yaml
from slugify import slugify

from movielog import db, humanize, imdb_http, viewings
from movielog.logger import logger

TABLE_NAME = "performing_credits"


@dataclass
class PerformingCredit(object):
    movie_imdb_id: str
    person_imdb_id: str
    person_name: str
    sequence: int
    roles: List[str]
    role_string: str
    notes: Optional[str]

    def __init__(
        self,
        movie_imdb_id: str,
        person_imdb_id: str,
        person_name: str,
        sequence: int,
        roles: List[str],
        notes: Optional[str],
    ) -> None:
        self.movie_imdb_id = movie_imdb_id
        self.person_imdb_id = person_imdb_id
        self.person_name = person_name
        self.sequence = sequence
        self.roles = roles
        self.notes = notes
        self.role_string = " / ".join(roles)

    @classmethod
    def from_imdb_http_cast_credit(
        cls, imdb_http_cast_credit: imdb_http.CastCredit
    ) -> "PerformingCredit":
        return cls(
            movie_imdb_id=imdb_http_cast_credit.movie_imdb_id,
            person_imdb_id=imdb_http_cast_credit.person_imdb_id,
            person_name=imdb_http_cast_credit.name,
            sequence=imdb_http_cast_credit.sequence,
            roles=imdb_http_cast_credit.roles,
            notes=imdb_http_cast_credit.notes,
        )

    def to_yaml(self) -> Any:
        return {
            "sequence": self.sequence,
            "person_imdb_id": self.person_imdb_id,
            "name": self.person_name,
            "roles": self.roles,
            "notes": self.notes,
        }


@dataclass
class Movie(object):
    imdb_id: str
    title: str
    year: str
    performing_credits: List[PerformingCredit]
    file_path: Optional[str]

    @classmethod
    def from_imdb_id(cls, imdb_id: str) -> "Movie":
        imdb_movie = imdb_http.get_movie(imdb_id)
        performing_credits = [
            PerformingCredit.from_imdb_http_cast_credit(cast_credit)
            for cast_credit in imdb_movie.cast_credits
        ]

        return Movie(
            imdb_id=imdb_id,
            title=imdb_movie.title,
            year=imdb_movie.year,
            performing_credits=performing_credits,
            file_path=None,
        )

    def save(self) -> str:
        file_path = self.file_path

        if not file_path:
            slug = slugify(self.title_with_year)
            file_path = os.path.join(TABLE_NAME, f"{slug}.yml")
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

        with open(file_path, "wb") as output_file:
            output_file.write(self.to_yaml())

        self.file_path = file_path

        logger.log(
            "Wrote {} with {} credits.",
            self.file_path,
            humanize.intcomma(len(self.performing_credits)),
        )

        return file_path

    @property
    def title_with_year(self) -> str:
        return f"{self.title} ({self.year})"

    def to_yaml(self) -> Any:

        return yaml.dump(
            {
                "imdb_id": self.imdb_id,
                "title": self.title_with_year,
                "cast": [
                    performing_credit.to_yaml()
                    for performing_credit in self.performing_credits
                ],
            },
            encoding="utf-8",
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )


class PerformingCreditsTable(db.Table):
    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "movie_imdb_id" varchar(255) NOT NULL
                REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "person_imdb_id" varchar(255) NOT NULL
                REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "sequence" INT NOT NULL,
            "roles" TEXT,
            "notes" TEXT,
            PRIMARY KEY (movie_imdb_id, person_imdb_id));
        """

    @classmethod
    def insert_performing_credits(
        cls, performing_credits: Sequence[PerformingCredit]
    ) -> None:
        ddl = """
        INSERT INTO {0}(movie_imdb_id, person_imdb_id, sequence, roles, notes)
        VALUES(:movie_imdb_id, :person_imdb_id, :sequence, :role_string, :notes);
        """.format(
            cls.table_name
        )

        cls.insert(
            ddl=ddl, parameter_seq=[asdict(credit) for credit in performing_credits]
        )
        cls.add_index("movie_imdb_id")
        cls.add_index("person_imdb_id")
        cls.validate(performing_credits)


@logger.catch
def update() -> None:
    logger.log("==== Begin updating {}...", TABLE_NAME)

    PerformingCreditsTable.recreate()

    performing_credits: List[PerformingCredit] = []
    imdb_ids = viewings.imdb_ids()

    for imdb_id in imdb_ids:
        movie = Movie.from_imdb_id(imdb_id)
        movie.save()
        performing_credits.extend(movie.performing_credits)

    PerformingCreditsTable.insert_performing_credits(performing_credits)


if __name__ == "__main__":
    update()
