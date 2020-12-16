import json
import os
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from typing import List

from movielog import db
from movielog.logger import logger

MAX_MOST_WATCHED = 20


@dataclass
class Movie(object):
    imdb_id: str
    title: str
    year: str
    decade: str
    slug: str


@dataclass
class Viewing(object):
    date: date
    venue: str
    sequence: str
    movie: Movie


@dataclass
class MostWatchedMovie(Movie):
    viewings: List[Viewing]
    viewing_count: int


@dataclass
class DecadeGroup(object):
    decade: str
    movie_count: int
    viewing_count: int
    viewings: List[Viewing]


@dataclass
class MovieYearStats(object):
    year: str
    movie_count: int
    viewing_count: int
    most_watched: List[MostWatchedMovie]
    decades: List[DecadeGroup]

    @classmethod
    def fetch_viewings(cls) -> List[Viewing]:
        query = """
        SELECT
            viewings.sequence
        , movies.title
        , movies.year
        , movies.imdb_id
        , slug
        , strftime('%Y', viewings.date) AS viewing_year
        , substr(movies.year, 1, 3) || '0s' AS movie_decade
        , viewings.date
        , viewings.venue
        FROM viewings
        INNER JOIN movies ON movies.imdb_id = viewings.movie_imdb_id
        LEFT JOIN reviews ON reviews.movie_imdb_id = movies.imdb_id
        ORDER BY
            viewing_year
        """

        rows = db.exec_query(query)

        return [
            Viewing(
                date=date.fromisoformat(row["date"]),
                venue=row["venue"],
                sequence=row["sequence"],
                movie=Movie(
                    imdb_id=row["imdb_id"],
                    title=row["title"],
                    year=row["year"],
                    decade=row["movie_decade"],
                    slug=row["slug"],
                ),
            )
            for row in rows
        ]

    @classmethod
    def generate_most_watched(cls, viewings: List[Viewing]) -> List[MostWatchedMovie]:
        most_watched_movies = []
        viewings_by_imdb_id = defaultdict(list)

        for viewing in viewings:
            viewings_by_imdb_id[viewing.movie.imdb_id].append(viewing)

        for viewing_group in viewings_by_imdb_id.values():
            if len(viewing_group) == 1:
                continue
            movie = viewing_group[0].movie
            most_watched_movies.append(
                MostWatchedMovie(
                    imdb_id=movie.imdb_id,
                    title=movie.title,
                    slug=movie.slug,
                    year=movie.year,
                    decade=movie.decade,
                    viewings=viewing_group,
                    viewing_count=len(viewing_group),
                )
            )

        return sorted(
            most_watched_movies, reverse=True, key=lambda movie: len(movie.viewings)
        )[:MAX_MOST_WATCHED]

    @classmethod
    def generate_decades(cls, viewings: List[Viewing]) -> List[DecadeGroup]:
        decades: List[DecadeGroup] = []
        viewings_by_decade = defaultdict(list)

        for viewing in viewings:
            viewings_by_decade[viewing.movie.decade].append(viewing)

        for viewing_group in viewings_by_decade.values():
            movie = viewing_group[0].movie
            decades.append(
                DecadeGroup(
                    decade=movie.decade,
                    movie_count=len(
                        set(group_item.movie.imdb_id for group_item in viewing_group)
                    ),
                    viewing_count=len(viewing_group),
                    viewings=viewing_group,
                )
            )

        return sorted(decades, key=lambda group: group.viewing_count, reverse=True)

    @classmethod
    def generate_for_viewing_year(
        cls, viewings: List[Viewing], year: int
    ) -> "MovieYearStats":
        viewings_for_year = list(
            filter(lambda viewing: viewing.date.year == year, viewings)
        )
        return MovieYearStats(
            year=str(year),
            movie_count=len(
                set(viewing.movie.imdb_id for viewing in viewings_for_year)
            ),
            viewing_count=len(viewings_for_year),
            most_watched=cls.generate_most_watched(viewings_for_year),
            decades=cls.generate_decades(viewings_for_year),
        )

    @classmethod
    def export_by_year_stats(cls, viewings: List[Viewing]):
        stats = []

        years = list(set(viewing.date.year for viewing in viewings))

        for year in years:
            stats.append(cls.generate_for_viewing_year(viewings, year))

        with open(
            os.path.join("export", "most_watched_movies_by_year.json"), "w"
        ) as output_file:
            output_file.write(json.dumps([asdict(stat) for stat in stats], default=str))

    @classmethod
    def export_rollup_stats(cls, viewings: List[Viewing]):
        allstats = asdict(
            MovieYearStats(
                year="all",
                movie_count=len(set(viewing.movie.imdb_id for viewing in viewings)),
                viewing_count=len(viewings),
                most_watched=cls.generate_most_watched(viewings),
                decades=cls.generate_decades(viewings),
            )
        )

        allstats.pop("year")
        os.makedirs(os.path.join("export", "most_watched_movies"), exist_ok=True)

        with open(
            os.path.join("export", "most_watched_movies", "index.json"), "w"
        ) as output_file:
            output_file.write(json.dumps(allstats, default=str))

    @classmethod
    def export(cls) -> None:
        viewings = cls.fetch_viewings()
        cls.export_by_year_stats(viewings)
        cls.export_rollup_stats(viewings)


def export() -> None:
    logger.log("==== Begin exporting {}...", "most watched movies")
    MovieYearStats.export()
