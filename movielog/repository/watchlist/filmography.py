from __future__ import annotations

import fnmatch
import re
import time
from typing import TYPE_CHECKING, Callable, Iterator, Optional, Union

import imdb

from movielog.moviedata import api as moviedata_api
from movielog.utils import list_tools
from movielog.utils.logging import logger
from movielog.watchlist.movies import JsonExcludedTitle, JsonTitle

if TYPE_CHECKING:
    from movielog.directors import Director
    from movielog.performers import Performer
    from movielog.person import Person
    from movielog.writer import Writer

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
        "Skipping {} for {} {}",
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
    validator: Callable[[imdb.Movie.Movie, Person], Optional[str]],
) -> Person:
    filmography: set[str] = set()

    if isinstance(person.imdbId, str):
        imdb_person = imdb_http.get_person(person.imdbId[2:])
        filmography = set(
            [movie.movieID for movie in filmography_for_person(imdb_person, key)]
        )
    else:
        filmographies: list[set[str]] = []
        for imdb_id in person.imdbId:
            imdb_person = imdb_http.get_person(imdb_id[2:])
            filmographies.append(
                set(movie.movieID for movie in filmography_for_person(imdb_person, key))
            )

        filmography = set.intersection(*filmographies)

    existing_title_ids = set([title["imdbId"][2:] for title in person.titles])

    missing_title_ids = existing_title_ids - filmography
    total_missing_title_ids = len(missing_title_ids)

    for index, missing_title_id in enumerate(missing_title_ids):
        missing_title = next(
            (
                title
                for title in person.titles
                if title["imdbId"][2:] == missing_title_id
            ),
            None,
        )

        if missing_title:
            person.titles.remove(missing_title)
            logger.log(
                "{}/{} missing title {} removed.",
                index + 1,
                total_missing_title_ids,
                missing_title_id,
            )

    existing_excluded_title_ids = set(
        [title["imdbId"][2:] for title in person.excludedTitles]
    )

    missing_excluded_title_ids = existing_excluded_title_ids - filmography
    total_missing_excluded_title_ids = len(missing_excluded_title_ids)

    for index, missing_excluded_title_id in enumerate(missing_excluded_title_ids):
        missing_excluded_title = next(
            (
                excluded_title
                for excluded_title in person.excludedTitles
                if excluded_title["imdbId"][2:] == missing_excluded_title_id
            ),
            None,
        )

        if missing_excluded_title:
            person.excludedTitles.remove(missing_excluded_title)
            logger.log(
                "{}/{} missing excluded title {} removed.",
                index + 1,
                total_missing_excluded_title_ids,
                missing_excluded_title_id,
            )

    total_filmography = len(filmography)

    for index, imdb_id in enumerate(filmography):
        excluded_title = next(
            (
                excluded_title
                for excluded_title in person.excludedTitles
                if excluded_title["imdbId"][2:] == imdb_id
            ),
            None,
        )

        if excluded_title:
            logger.log(
                "{0}/{1} {2} already in {3}.".format(
                    index + 1,
                    total_filmography,
                    excluded_title["title"],
                    "excludedTitles",
                ),
            )
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
            logger.log(
                "{0}/{1} {2} already in {3}.".format(
                    index + 1,
                    total_filmography,
                    existing_title["title"],
                    "titles",
                )
            )
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

        if imdb_movie["kind"] not in {
            "movie",
            "tv movie",
            "video movie",
        }:
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
                    reason=imdb_movie["kind"],
                )
            )
            logger.log(
                "{}/{} {} added to {} ({}).",
                index + 1,
                total_filmography,
                imdb_movie["long imdb title"],
                "excludedTitles",
                imdb_movie["kind"],
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
            logger.log(
                "{}/{} {} added to {} ({}).",
                index + 1,
                total_filmography,
                imdb_movie["long imdb title"],
                "excludedTitles",
                "{0}".format(", ".join(invalid_genres)),
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
            logger.log(
                "{}/{} {} added to {} ({}).",
                index + 1,
                total_filmography,
                imdb_movie["long imdb title"],
                "excludedTitles",
                "silent",
            )
            continue

        invalid_notes = validator(imdb_movie, person)
        if invalid_notes:
            person.excludedTitles.append(
                JsonExcludedTitle(
                    imdbId="tt{0}".format(imdb_movie.movieID),
                    title=imdb_movie["long imdb title"],
                    reason=invalid_notes,
                )
            )
            logger.log(
                "{}/{} {} added to {} ({}).",
                index + 1,
                total_filmography,
                imdb_movie["long imdb title"],
                "excludedTitles",
                invalid_notes,
            )
            continue

        person.titles.append(
            JsonTitle(
                imdbId="tt{0}".format(imdb_movie.movieID),
                title=imdb_movie["long imdb title"],
            )
        )
        logger.log(
            "{}/{} {} added to {}.",
            index + 1,
            total_filmography,
            imdb_movie["long imdb title"],
            "titles",
        )

    person.titles = sorted(person.titles, key=lambda title: title_sort_key(title))

    person.excludedTitles = sorted(
        person.excludedTitles, key=lambda title: title_sort_key(title)
    )

    return person


def title_sort_key(title: Union[JsonTitle, JsonExcludedTitle]) -> str:
    year_sort_regex = r"\(\d*\)"

    year = re.search(year_sort_regex, title["title"])

    if year:
        return "{0}-{1}".format(year.group(0), title["imdbId"])

    return "(????)-{0}".format(title["imdbId"])


def build_movie(imdb_movie: imdb.Movie.Movie) -> Movie:
    return Movie(
        imdb_id="tt{0}".format(imdb_movie.movieID),
        year=imdb_movie["year"],
        title=imdb_movie["title"],
        notes=None if imdb_movie.notes == "" else imdb_movie.notes,
        kind=imdb_movie["kind"],
    )


def valid_for_director(imdb_movie: imdb.Movie.Movie, person: Person) -> Optional[str]:
    director_notes = set(
        [
            credit.notes
            for credit in imdb_movie.get("directors", [])
            if "nm{0}".format(credit.personID) in person.imdbId
        ]
    )

    imdb_movie.notes = " / ".join(director_notes)

    if not moviedata_api.valid_director_notes(imdb_movie):
        return imdb_movie.notes

    return None


def valid_for_performer(imdb_movie: imdb.Movie.Movie, person: Person) -> Optional[str]:
    performer_notes = set(
        [
            credit.notes
            for credit in imdb_movie.get("cast", [])
            if "nm{0}".format(credit.personID) in person.imdbId
        ]
    )

    imdb_movie.notes = " / ".join(performer_notes)

    if not moviedata_api.valid_cast_notes(imdb_movie):
        return imdb_movie.notes

    return None


def valid_for_writer(imdb_movie: imdb.Movie.Movie, person: Person) -> Optional[str]:
    writer_notes = set(
        [
            credit.notes
            for credit in imdb_movie.get("writers", [])
            if "nm{0}".format(credit.personID) in person.imdbId
        ]
    )

    imdb_movie.notes = " / ".join(writer_notes)

    if not moviedata_api.valid_writer_notes(imdb_movie):
        return imdb_movie.notes

    return None


def for_director(director: Director) -> Director:
    return valid_movies_for_person(director, "director", valid_for_director)

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


def for_writer(writer: Writer) -> Writer:
    return valid_movies_for_person(writer, "writer", valid_for_writer)


def for_performer(performer: Performer) -> Performer:
    return valid_movies_for_person(performer, "performer", valid_for_performer)
