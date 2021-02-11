import json
import os
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from typing import Sequence

from movielog import db
from movielog.logger import logger

MAX_MOST_WATCHED = 20


@dataclass
class Person(object):
    imdb_id: str
    full_name: str
    slug: str


@dataclass
class Movie(object):
    imdb_id: str
    title: str
    year: str
    decade: str
    slug: str


@dataclass
class ViewingWithPerson(object):
    date: date
    venue: str
    sequence: str
    movie: Movie
    person: Person


@dataclass
class MostWatchedPerson(Person):
    movie_count: int
    viewings: Sequence[ViewingWithPerson]
    viewing_count: int


@dataclass
class PersonYearStats(object):
    year: str
    most_watched: Sequence[MostWatchedPerson]

    @classmethod
    def exclude_person_ids_query_clause(cls) -> str:
        ids_to_exclude = [
            "nm0498278",  # Stan Lee
            "nm0456158",  # Jack Kirby
            "nm4160687",  # Jim Starlin
            "nm0800209",  # Joe Simon
            "nm1293367",  # Larry Lieber
            "nm1921680",  # Steve Englehart
            "nm3238648",  # Steve Gan
            "nm2757098",  # Bill Mantlo
            "nm0317493",  # Keith Giffen
            "nm1411347",  # Don Heck
        ]

        exclude_strings = []

        for person_id in ids_to_exclude:
            exclude_strings.append('person_imdb_id != "{0}"'.format(person_id))

        return " AND ".join(exclude_strings)

    @classmethod
    def fetch_viewings_query(cls, credit_table: str, credit_table_key: str) -> str:
        query = """
            SELECT
            viewings.sequence
            , movies.title
            , movies.year
            , movies.imdb_id
            , strftime('%Y', viewings.date) AS viewing_year
            , substr(movies.year, 1, 3) || '0s' AS movie_decade
            , viewings.date
            , viewings.venue
            , person_imdb_id
            , full_name
            , watchlist.slug AS person_slug
            , reviews.slug AS review_slug
            FROM viewings
            LEFT JOIN movies ON viewings.movie_imdb_id = movies.imdb_id
            LEFT JOIN {0} ON {0}.movie_imdb_id = viewings.movie_imdb_id
            LEFT JOIN people ON person_imdb_id = people.imdb_id
            LEFT JOIN reviews ON viewings.movie_imdb_id = reviews.movie_imdb_id
            LEFT JOIN (
                SELECT
                    reviews.movie_imdb_id
                , {1}
                , watchlist.slug
                FROM reviews
                INNER JOIN watchlist ON reviews.movie_imdb_id = watchlist.movie_imdb_id
                GROUP BY {1}
            ) AS watchlist ON watchlist.{1} = person_imdb_id
            WHERE {2}
            GROUP BY
                viewings.sequence
                , person_imdb_id
        """

        return query.format(
            credit_table, credit_table_key, cls.exclude_person_ids_query_clause()
        )

    @classmethod
    def fetch_viewings(cls, query: str) -> Sequence[ViewingWithPerson]:
        rows = db.exec_query(query)

        return [
            ViewingWithPerson(
                date=date.fromisoformat(row["date"]),
                venue=row["venue"],
                sequence=row["sequence"],
                movie=Movie(
                    imdb_id=row["imdb_id"],
                    title=row["title"],
                    year=row["year"],
                    decade=row["movie_decade"],
                    slug=row["review_slug"],
                ),
                person=Person(
                    imdb_id=row["person_imdb_id"],
                    full_name=row["full_name"],
                    slug=row["person_slug"],
                ),
            )
            for row in rows
        ]

    @classmethod
    def generate_for_viewing_year(
        cls, viewings: Sequence[ViewingWithPerson], year: int
    ) -> "PersonYearStats":
        viewings_for_year = list(
            filter(lambda viewing: viewing.date.year == year, viewings)
        )
        return PersonYearStats(
            year=str(year),
            most_watched=cls.generate_most_watched(viewings_for_year),
        )

    @classmethod
    def generate_most_watched(
        cls, viewings: Sequence[ViewingWithPerson]
    ) -> Sequence[MostWatchedPerson]:
        most_watched_people = []
        people_by_imdb_id = defaultdict(list)

        for viewing in viewings:
            people_by_imdb_id[viewing.person.imdb_id].append(viewing)

        for person_group in people_by_imdb_id.values():
            if len(person_group) == 1:
                continue
            person = person_group[0].person
            most_watched_people.append(
                MostWatchedPerson(
                    imdb_id=person.imdb_id,
                    full_name=person.full_name,
                    slug=person.slug,
                    movie_count=len(
                        list(
                            set(
                                [
                                    person_group_item.movie.imdb_id
                                    for person_group_item in person_group
                                ]
                            )
                        )
                    ),
                    viewing_count=len(person_group),
                    viewings=person_group,
                )
            )

        return sorted(
            most_watched_people, reverse=True, key=lambda movie: len(movie.viewings)
        )[:MAX_MOST_WATCHED]

    @classmethod
    def export_by_year_stats(
        cls, viewings: Sequence[ViewingWithPerson], output_file_name: str
    ):
        stats = []

        years = list(set(viewing.date.year for viewing in viewings))

        for year in years:
            stats.append(cls.generate_for_viewing_year(viewings, year))

        with open(os.path.join("export", output_file_name), "w") as output_file:
            output_file.write(json.dumps([asdict(stat) for stat in stats], default=str))

    @classmethod
    def export_rollup_stats(
        cls, viewings: Sequence[ViewingWithPerson], folder_name: str
    ):
        allstats = asdict(
            cls(
                year="all",
                most_watched=cls.generate_most_watched(viewings),
            )
        )

        allstats.pop("year")
        os.makedirs(os.path.join("export", folder_name), exist_ok=True)

        with open(
            os.path.join("export", folder_name, "index.json"), "w"
        ) as output_file:
            output_file.write(json.dumps(allstats, default=str))


@dataclass
class DirectorYearStats(PersonYearStats):
    @classmethod
    def export(cls) -> None:
        viewings = cls.fetch_viewings(
            cls.fetch_viewings_query(
                credit_table="directing_credits", credit_table_key="director_imdb_id"
            )
        )

        cls.export_by_year_stats(viewings, "most_watched_directors_by_year.json")
        cls.export_rollup_stats(viewings, "most_watched_directors")


@dataclass
class PerformerYearStats(PersonYearStats):
    @classmethod
    def export(cls) -> None:
        viewings = cls.fetch_viewings(
            cls.fetch_viewings_query(
                credit_table="performing_credits", credit_table_key="performer_imdb_id"
            )
        )

        cls.export_by_year_stats(viewings, "most_watched_performers_by_year.json")
        cls.export_rollup_stats(viewings, "most_watched_performers")


@dataclass
class WriterYearStats(PersonYearStats):
    @classmethod
    def export(cls) -> None:
        viewings = cls.fetch_viewings(
            cls.fetch_viewings_query(
                credit_table="writing_credits", credit_table_key="writer_imdb_id"
            )
        )

        cls.export_by_year_stats(viewings, "most_watched_writers_by_year.json")
        cls.export_rollup_stats(viewings, "most_watched_writers")


def log_heading(heading: str) -> None:
    logger.log("==== Begin exporting {}...", heading)


def export() -> None:
    log_heading("most watched directors")
    DirectorYearStats.export()
    log_heading("most watched performers")
    PerformerYearStats.export()
    log_heading("most watched writers")
    WriterYearStats.export()
