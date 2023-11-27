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

Whitelist = {
    "tt0019035",  # Interference (1928) [no runtime]
    "tt0116671",  # Jack Frost (1997) [V]
    "tt0148615",  # Play Motel (1979) [X]
    "tt1801096",  # Sexy Evil Genius (2013) [V]
    "tt0093135",  # Hack-O-Lantern (1988) [V]
    "tt11060882",  # Batman: The Dark Knight Returns (2013) [V]
    "tt0101760",  # Door to Silence (1992) [V]
    "tt0112643",  # Castle Freak (1995) [V]
    "tt1356864",  # I'm Still Here (2010) [documentary]
    "tt0209095",  # Leprechaun 5: In the Hood [V]
    "tt0239496",  # Jack Frost 2 (2000) [V]
    "tt0094762",  # Blood Delerium (1988) (no year)
    "tt0113636",  # Leprechaun 3 [V]
    "tt22698070",  # Mortal Kombat Legends: Cage Match [V]
    "tt0114397",  # The Setup [Showtime TV Movie]
    "tt0242798",  # Proximity (2001) [HBO TV Movie]
    "tt0106449",  # Body Bags (1993) [Showtime TV Movie]
    "tt0070696",  # The Sinful Dwarf (1973) [X]
}


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
        filmography["performer"] = filmography.pop(
            "actor",
            [],
        ) + filmography.pop(
            "actress",
            [],
        )

    return reversed(filmography.get(key, []))


def has_invalid_movie_id(imdb_movie: imdb.Movie.Movie) -> bool:
    valid_imdb_ids = moviedata_api.movie_ids()
    movie_id = "tt{0}".format(imdb_movie.movieID)

    return movie_id not in valid_imdb_ids


def is_valie_feature(imdb_movie: imdb.Movie.Movie) -> bool:
    if "tt{0}".format(imdb_movie.movieID) in Whitelist:
        return True

    return (
        imdb_movie["kind"] == "movie"
        and "Adult" not in imdb_movie["genres"]
        and "Short" not in imdb_movie["genres"]
        and "Documentary" not in imdb_movie["genres"]
    )


def valid_movies_for_person(  # noqa: WPS231
    person_imdb_id: str, key: str
) -> Iterator[tuple[imdb.Person.Person, imdb.Movie.Movie]]:
    imdb_person = imdb_http.get_person(person_imdb_id[2:])

    for imdb_movie in filmography_for_person(imdb_person, key):
        imdb_movie = imdb_http.get_movie(imdb_movie.movieID)

        if "tt{0}".format(imdb_movie.movieID) in Whitelist:
            yield (imdb_person, imdb_movie)

        if imdb_movie["kind"] != "movie":
            log_skip(
                imdb_person=imdb_person,
                imdb_movie=imdb_movie,
                reason="(tt{0} kind is {1})".format(
                    imdb_movie.movieID, imdb_movie["kind"]
                ),
            )
            continue

        skipped = False
        for invalid_genre in ["Adult", "Short", "Documentary"]:
            if invalid_genre in imdb_movie["genres"]:
                log_skip(
                    imdb_person=imdb_person,
                    imdb_movie=imdb_movie,
                    reason="(tt{0} genres includes {1})".format(
                        imdb_movie.movieID, invalid_genre
                    ),
                )
                skipped = True

        if skipped:
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
        director_notes = [
            credit.notes
            for credit in imdb_movie["directors"]
            if credit.personID == person_imdb_id[2:]
        ]

        imdb_movie.notes = " / ".join(director_notes)

        if not moviedata_api.valid_director_notes(imdb_movie):
            log_skip(
                imdb_person=imdb_person,
                imdb_movie=imdb_movie,
                reason="({0})".format(imdb_movie.notes),
            )
            continue

        movie_list.append(build_movie(imdb_movie))

    return movie_list


def for_writer(person_imdb_id: str) -> list[Movie]:
    movie_list: list[Movie] = []

    for imdb_person, imdb_movie in valid_movies_for_person(person_imdb_id, "writer"):
        writer_notes = [
            credit.notes
            for credit in imdb_movie["writers"]
            if credit.personID == person_imdb_id[2:]
        ]

        imdb_movie.notes = " / ".join(writer_notes)

        if not moviedata_api.valid_writer_notes(imdb_movie):
            log_skip(
                imdb_person=imdb_person,
                imdb_movie=imdb_movie,
                reason="({0})".format(imdb_movie.notes),
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
                reason="({0})".format(imdb_movie.notes),
            )
            continue

        movie_list.append(build_movie(imdb_movie))

    return movie_list
