import fnmatch
from collections import ChainMap
from dataclasses import dataclass
from typing import Optional, Set

import imdb

silent_ids: Set[str] = set()
no_sound_mix_ids: Set[str] = set()
imdb_scraper = imdb.IMDb(reraiseExceptions=True)


@dataclass
class Movie(object):  # noqa: WPS230
    year: str
    title: str
    imdb_id: str
    movie_object: imdb.Movie.Movie
    notes: str
    in_production: bool = False
    is_silent: Optional[bool] = None
    has_sound_mix: Optional[bool] = None

    @classmethod
    def from_imdb_movie(cls, imdb_movie: imdb.Movie.Movie) -> "Movie":
        movie = Movie(
            year=imdb_movie.get("year", "????"),
            title=imdb_movie["title"],
            imdb_id=f"tt{imdb_movie.movieID}",
            movie_object=imdb_movie,
            notes=imdb_movie.notes,
        )

        in_production = imdb_movie.get("status")
        if in_production:
            movie.in_production = True
            movie.notes = f"({in_production})"

        if movie.imdb_id in no_sound_mix_ids:
            movie.has_sound_mix = False
        elif movie.imdb_id in silent_ids:
            movie.has_sound_mix = True
            movie.is_silent = True
        else:
            imdb_scraper.update(movie.movie_object, info=["technical"])
            if movie_has_sound_mix(movie):
                movie.has_sound_mix = True
                movie.is_silent = movie_is_silent(movie)
            else:
                movie.has_sound_mix = False
                movie.is_silent = None

        return movie


class Person(object):
    def __init__(self, imdb_id: str) -> None:
        self.imdb_id = imdb_id
        imdb_person = imdb_scraper.get_person(imdb_id[2:])
        self.name = imdb_person["name"]
        self.filmography = dict(ChainMap(*imdb_person["filmography"]))
        self.filmography["performer"] = self.filmography.get(
            "actor", [],
        ) + self.filmography.get("actress", [],)


def movie_has_sound_mix(movie: Movie) -> bool:
    if movie.imdb_id in no_sound_mix_ids:
        return False

    if "sound mix" in movie.movie_object["technical"]:
        return True

    no_sound_mix_ids.add(movie.imdb_id)

    return False


def movie_is_silent(movie: Movie) -> bool:
    if movie.imdb_id in silent_ids:
        return True

    pattern = "Silent*"

    sound_mixes = movie.movie_object["technical"]["sound mix"]
    if fnmatch.filter(sound_mixes, pattern):
        silent_ids.add(movie.imdb_id)
        return True

    return False
