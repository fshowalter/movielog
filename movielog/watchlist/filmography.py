from __future__ import annotations

import fnmatch
import re
import time
from typing import TYPE_CHECKING, Callable, Iterator, Optional

import imdb

from movielog.moviedata import api as moviedata_api
from movielog.utils import list_tools
from movielog.utils.logging import logger
from movielog.watchlist.movies import JsonExcludedTitle, JsonTitle

if TYPE_CHECKING:
    from movielog.directors import Director
    from movielog.person import Person

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
    # movie_id = imdb_movie.movieID

    # if movie_id in silent_ids:
    #     return True

    # if movie_id in no_sound_mix_ids:
    #     return None

    # imdb_http.update(imdb_movie, info=["technical"])

    # if "sound mix" not in imdb_movie["technical"]:
    #     no_sound_mix_ids.add(movie_id)
    #     return None

    # pattern = "Silent*"

    # sound_mixes = imdb_movie["technical"]["sound mix"]
    # if fnmatch.filter(sound_mixes, pattern):
    #     silent_ids.add(movie_id)
    #     return True

    # return False

    return "Silent" in imdb_movie.get("sound mix", [])


def log_skip(person_name: str, imdb_movie: imdb.Movie.Movie, reason: str) -> None:
    logger.log(
        "Skipping {0} for {1} {2}",
        imdb_movie["long imdb title"],
        person_name,
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
    # if "tt{0}".format(imdb_movie.movieID) in Whitelist:
    #     return True
    return (
        "Adult" not in imdb_movie["genres"]
        and "Short" not in imdb_movie["genres"]
        and "Documentary" not in imdb_movie["genres"]
    )


def valid_movies_for_person(  # noqa: WPS231
    person: Person,
    key: str,
    validator: Callable[[imdb.Movie.Movie, str], Optional[str]],
) -> Person:
    filmography: set[str] = {}

    if len(person.imdbIds) == 1:
        imdb_person = imdb_http.get_person(person.imdbIds[0][2:])
        filmography = set(
            [movie.movieID for movie in filmography_for_person(imdb_person, key)]
        )
    else:
        filmographies: list[set[str]] = []
        for imdb_id in person.imdbIds:
            imdb_person = imdb_http.get_person(imdb_id)
            filmographies.append(
                set(movie.movieID for movie in filmography_for_person(imdb_person, key))
            )

        filmography = set.intersection(*filmographies)

    for imdb_id in filmography:
        excluded_title = next(
            (
                excluded_title
                for excluded_title in person.excludedTitles
                if excluded_title["imdbId"][2:] == imdb_id
            ),
            None,
        )

        if excluded_title:
            continue

        existing_title = next(
            (
                included_title
                for included_title in person.titles
                if included_title["imdbId"][2:] == imdb_id
            ),
            None,
        )

        if existing_title:
            continue

        imdb_movie = imdb_http.get_movie(imdb_id)

        # if "tt{0}".format(imdb_movie.movieID) in Whitelist:
        #     yield (imdb_person, imdb_movie)

        if imdb_movie.get("production status", None):
            log_skip(
                person_name=person.name,
                imdb_movie=imdb_movie,
                reason="(tt{0} production status {1})".format(
                    imdb_movie.movieID, imdb_movie["production status"]
                ),
            )
            continue

        if imdb_movie["kind"] in {"tv series", "music video", "tv mini series"}:
            # log_skip(
            #     imdb_person=imdb_person,
            #     imdb_movie=imdb_movie,
            #     reason="(tt{0} kind is {1})".format(
            #         imdb_movie.movieID, imdb_movie["kind"]
            #     ),
            # )
            person.excludedTitles.append(
                JsonExcludedTitle(
                    imdbId="tt{0}".format(imdb_movie.movieID),
                    title=imdb_movie["long imdb title"],
                    reason="{0}".format(imdb_movie["kind"]),
                )
            )
            continue

        invalid_genres = {"Adult", "Short", "Documentary"} & set(
            imdb_movie.get("genres", [])
        )
        if invalid_genres:
            # log_skip(
            #     imdb_person=imdb_person,
            #     imdb_movie=imdb_movie,
            #     reason="(tt{0} genres include {1})".format(
            #         imdb_movie.movieID, ", ".join(invalid_genres)
            #     ),
            # )
            person.excludedTitles.append(
                JsonExcludedTitle(
                    imdbId="tt{0}".format(imdb_movie.movieID),
                    title=imdb_movie["long imdb title"],
                    reason="{0}".format(", ".join(invalid_genres)),
                )
            )
            continue

        if is_silent(imdb_movie):
            # log_skip(
            #     imdb_person=imdb_person,
            #     imdb_movie=imdb_movie,
            #     reason="(tt{0} sound mix is silent)".format(imdb_movie.movieID),
            # )
            person.excludedTitles.append(
                JsonExcludedTitle(
                    imdbId="tt{0}".format(imdb_movie.movieID),
                    title=imdb_movie["long imdb title"],
                    reason="silent",
                )
            )
            continue

        invalid_notes = validator(imdb_movie, person.imdbId)
        if invalid_notes:
            person.excludedTitles.append(
                JsonExcludedTitle(
                    imdbId="tt{0}".format(imdb_movie.movieID),
                    title=imdb_movie["long imdb title"],
                    reason=invalid_notes,
                )
            )
            continue

        person.titles.append(
            JsonTitle(
                imdbId="tt{0}".format(imdb_movie.movieID),
                title=imdb_movie["long imdb title"],
            )
        )

    person.titles = sorted(
        person.titles, key=lambda title: title_sort_key(title["title"])
    )

    person.excludedTitles = sorted(
        person.excludedTitles, key=lambda title: title_sort_key(title["title"])
    )

    return person


def title_sort_key(title: str) -> str:
    year_sort_regex = r"\(\d*\)"

    year = re.search(year_sort_regex, title)

    if year:
        return year.group(0)

    return "(????)"


def build_movie(imdb_movie: imdb.Movie.Movie) -> Movie:
    return Movie(
        imdb_id="tt{0}".format(imdb_movie.movieID),
        year=imdb_movie["year"],
        title=imdb_movie["title"],
        notes=None if imdb_movie.notes == "" else imdb_movie.notes,
        kind=imdb_movie["kind"],
    )


def valid_for_director(
    imdb_movie: imdb.Movie.Movie, person_imdb_id: str
) -> Optional[str]:
    director_notes = [
        credit.notes
        for credit in imdb_movie.get("directors", [])
        if credit.personID == person_imdb_id[2:]
    ]

    imdb_movie.notes = " / ".join(director_notes)

    if not moviedata_api.valid_director_notes(imdb_movie):
        return imdb_movie.notes

    return None


def for_director(director: Director) -> Director:
    valid_movies_for_person(director, "director", valid_for_director)

    return director
    # ):
    #     # director_notes = [
    #     #     credit.notes
    #     #     for credit in imdb_movie.get("directors", [])
    #     #     if credit.personID == person_imdb_id[2:]
    #     # ]

    #     # imdb_movie.notes = " / ".join(director_notes)

    #     # if not moviedata_api.valid_director_notes(imdb_movie):
    #     #     log_skip(
    #     #         imdb_person=imdb_person,
    #     #         imdb_movie=imdb_movie,
    #     #         reason="({0})".format(imdb_movie.notes),
    #     #     )
    #     #     continue

    #     movie_list.append(build_movie(imdb_movie))
    #     excluded_movies = excluded_titles

    # return movie_list, excluded_movies


def for_writer(person_imdb_id: str) -> tuple[list[Movie], list[ExcludedTitle]]:
    movie_list: list[Movie] = []
    excluded_movies = []

    for imdb_person, imdb_movie, excluded_titles in valid_movies_for_person(
        person_imdb_id, "writer"
    ):
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
        excluded_movies = excluded_titles

    return movie_list, excluded_movies


def for_performer(person_imdb_id: str) -> tuple[list[Movie], list[ExcludedTitle]]:
    movie_list: list[Movie] = []
    excluded_movies = []

    for imdb_person, imdb_movie, excluded_titles in valid_movies_for_person(
        person_imdb_id, "performer"
    ):
        if not moviedata_api.valid_cast_notes(imdb_movie):
            log_skip(
                imdb_person=imdb_person,
                imdb_movie=imdb_movie,
                reason="({0})".format(imdb_movie.notes),
            )
            continue

        movie_list.append(build_movie(imdb_movie))
        excluded_movies = excluded_titles

    return movie_list, excluded_movies
