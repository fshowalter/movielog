from __future__ import annotations

import fnmatch
import time
from typing import Iterator, Optional

import imdb

from movielog.moviedata import api as moviedata_api
from movielog.utils.logging import logger
from movielog.watchlist.movies import Movie

imdb_http = imdb.IMDb(reraiseExceptions=True)
silent_ids: set[str] = set()
no_sound_mix_ids: set[str] = set()


def is_silent(imdb_movie: imdb.Movie.Movie) -> Optional[bool]:
    movie_id = imdb_movie.movieID

    if movie_id in silent_ids:
        return True

    if movie_id in no_sound_mix_ids:
        return None

    time.sleep(1)
    imdb_http.update(imdb_movie, info=["technical"])

    if "sound mix" not in imdb_movie["technical"]:
        no_sound_mix_ids.add(movie_id)
        return None

    pattern = "Silent*"

    sound_mixes = imdb_movie["technical"]["sound mix"]
    if fnmatch.filter(sound_mixes, pattern):
        silent_ids.add(movie_id)
        return True

    return False


def log_skip(
    imdb_person: imdb.Person.Person, imdb_movie: imdb.Movie.Movie, reason: str
) -> None:
    logger.log(
        "Skipping {0} ({1}) for {2} {3}",
        imdb_movie["title"],
        imdb_movie.get("year", "????"),
        imdb_person["name"],
        reason,
    )


def production_status(imdb_movie: imdb.Movie.Movie) -> Optional[str]:
    status = imdb_movie.get("status")
    if status:
        return str(status)

    return None


def filmography_for_person(
    imdb_person: imdb.Person.Person, key: str
) -> Iterator[imdb.Movie.Movie]:
    filmography = imdb_person["filmography"]

    if key == "performer":
        filmography["performer"] = filmography.pop("actor", [],) + filmography.pop(
            "actress",
            [],
        )

    return reversed(filmography.get(key, []))


def has_invalid_movie_id(imdb_movie: imdb.Movie.Movie) -> bool:
    valid_imdb_ids = moviedata_api.movie_ids()
    movie_id = "tt{0}".format(imdb_movie.movieID)

    return movie_id not in valid_imdb_ids


def valid_movies_for_person(  # noqa: WPS231
    person_imdb_id: str, key: str
) -> Iterator[tuple[imdb.Person.Person, imdb.Movie.Movie]]:
    imdb_person = imdb_http.get_person(person_imdb_id[2:])

    for imdb_movie in filmography_for_person(imdb_person, key):
        if has_invalid_movie_id(imdb_movie):
            log_skip(
                imdb_person=imdb_person,
                imdb_movie=imdb_movie,
                reason="({0} not found in database)".format(imdb_movie.movieID),
            )
            continue

        if is_silent(imdb_movie):
            log_skip(
                imdb_person=imdb_person,
                imdb_movie=imdb_movie,
                reason="(silent movie)",
            )
            continue

        if production_status(imdb_movie):
            log_skip(
                imdb_person=imdb_person,
                imdb_movie=imdb_movie,
                reason="({0})".format(production_status(imdb_movie)),
            )
            continue

        yield (imdb_person, imdb_movie)


def build_movie(imdb_movie: imdb.Movie.Movie) -> Movie:
    return Movie(
        imdb_id="tt{0}".format(imdb_movie.movieID),
        year=imdb_movie["year"],
        title=imdb_movie["title"],
        notes=imdb_movie.notes,
    )


def for_director(person_imdb_id: str) -> list[Movie]:
    movie_list: list[Movie] = []

    for imdb_person, imdb_movie in valid_movies_for_person(person_imdb_id, "director"):
        if not moviedata_api.valid_director_notes(imdb_movie):
            log_skip(
                imdb_person=imdb_person,
                imdb_movie=imdb_movie,
                reason="({0})".format(imdb_movie["notes"]),
            )
            continue

        movie_list.append(build_movie(imdb_movie))

    return movie_list


def for_writer(person_imdb_id: str) -> list[Movie]:
    movie_list: list[Movie] = []

    for imdb_person, imdb_movie in valid_movies_for_person(person_imdb_id, "writer"):
        if not moviedata_api.valid_writer_notes(imdb_movie):
            log_skip(
                imdb_person=imdb_person,
                imdb_movie=imdb_movie,
                reason="({0})".format(imdb_movie["notes"]),
            )
            continue

        movie_list.append(build_movie(imdb_movie))

    return movie_list


def for_performer(person_imdb_id: str) -> list[Movie]:
    movie_list: list[Movie] = []

    for imdb_person, imdb_movie in valid_movies_for_person(person_imdb_id, "performer"):
        if not moviedata_api.valid_cast_notes(imdb_movie):
            log_skip(
                imdb_person=imdb_person,
                imdb_movie=imdb_movie,
                reason="({0})".format(imdb_movie["notes"]),
            )
            continue

        movie_list.append(build_movie(imdb_movie))

    return movie_list
