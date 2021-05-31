from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Optional

import imdb


@dataclass
class ReleaseDate(object):
    date: date
    notes: Optional[str]


def parse_json_date(json_date: str) -> Optional[date]:
    try:
        return datetime.strptime(json_date, "%d %B %Y").date()  # noqa: WPS323
    except ValueError:
        try:  # noqa: WPS505
            return datetime.strptime(json_date, "%B %Y").date()
        except ValueError:
            return None


def no_release_date(imdb_movie: imdb.Movie.Movie) -> ReleaseDate:
    return ReleaseDate(
        date=date(imdb_movie.get("year"), 1, 1),
        notes="No release date",
    )


def parse_release_dates(raw_release_dates: list[Dict[str, str]]) -> list[ReleaseDate]:
    release_dates: list[ReleaseDate] = []

    for release_date_json in raw_release_dates:
        release_date = parse_json_date(release_date_json.get("date", "").strip())

        if not release_date:
            continue

        release_dates.append(
            ReleaseDate(
                date=release_date,
                notes=release_date_json.get("notes", "").strip(),
            )
        )

    return release_dates


def parse(imdb_movie: imdb.Movie.Movie) -> ReleaseDate:
    raw_release_dates = imdb_movie.get("raw release dates")

    if not raw_release_dates:
        return no_release_date(imdb_movie)

    release_dates = parse_release_dates(raw_release_dates)

    if not release_dates:
        return no_release_date(imdb_movie)

    most_recent = sorted(release_dates, key=lambda rd: rd.date)[0]

    if most_recent.date.year != int(imdb_movie.get("year")):
        return ReleaseDate(
            date=date(imdb_movie.get("year"), 1, 1),
            notes="Given release date: {0} {1}".format(
                most_recent.date.isoformat(), most_recent.notes
            ),
        )

    return most_recent
