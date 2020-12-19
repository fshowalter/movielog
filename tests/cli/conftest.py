from typing import Callable, Generator, List

import pytest
from prompt_toolkit.application.current import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.input.posix_pipe import PipeInput

from movielog import movies, people
from tests.cli.typehints import CreditTuple, MovieTuple


@pytest.fixture(autouse=True, scope="function")
def mock_input() -> Generator[PipeInput, None, None]:
    pipe_input = create_pipe_input()
    with create_app_session(input=pipe_input):
        yield pipe_input
    pipe_input.close()


class SeedMovieBuilder(object):
    def __init__(self, movie_tuples: List[MovieTuple]) -> None:  # noqa: WPS231
        self.movies: List[movies.Movie] = []
        self.people: List[people.Person] = []

        for movie_tuple in movie_tuples:
            title = movie_tuple[1]

            movie = movies.Movie(
                imdb_id=movie_tuple[0],
                title=title,
                original_title=title,
                year=str(movie_tuple[2]),
                runtime_minutes=None,
                principal_cast=[],
            )

            for index, person in enumerate(movie_tuple[3]):
                movie.principal_cast.append(
                    movies.Principal(
                        movie_imdb_id=movie_tuple[0],
                        person_imdb_id=person[0],
                        sequence=index,
                        category=None,
                        job=None,
                        characters=None,
                    )
                )

                if any(person[0] == existing.imdb_id for existing in self.people):
                    continue

                if person[1] == "UNKNOWN":
                    continue

                self.people.append(
                    people.Person(
                        imdb_id=person[0],
                        full_name=person[1],
                        birth_year=None,
                        death_year=None,
                        primary_profession=None,
                        known_for_title_ids=None,
                    )
                )

            self.movies.append(movie)


@pytest.fixture
def seed_movies() -> Callable[[List[MovieTuple]], None]:
    def _seed_movies(movie_tuples: List[MovieTuple]) -> None:
        seed_movies = SeedMovieBuilder(movie_tuples)

        people.PeopleTable.recreate()
        people.PeopleTable.insert_people(seed_movies.people)
        movies.MoviesTable.recreate()
        movies.MoviesTable.insert_movies(seed_movies.movies)

    return _seed_movies


class SeedPersonWithCreditsBuilder(object):
    def __init__(self, credit_tuples: List[CreditTuple]) -> None:
        self.movies = []
        self.people = []

        for credit_tuple in credit_tuples:
            person = people.Person(
                imdb_id=credit_tuple[0],
                full_name=credit_tuple[1],
                birth_year=None,
                death_year=None,
                primary_profession=None,
                known_for_title_ids="",
            )

            for movie_tuple in credit_tuple[2]:
                title = movie_tuple[1]
                movie = movies.Movie(
                    imdb_id=movie_tuple[0],
                    title=title,
                    original_title=title,
                    year=str(movie_tuple[2]),
                    runtime_minutes=None,
                    principal_cast=[],
                )

                person.known_for_title_ids = (
                    f"{person.known_for_title_ids},{movie.imdb_id}"
                )

                self.movies.append(movie)
            self.people.append(person)


@pytest.fixture
def seed_people() -> Callable[[List[CreditTuple]], None]:
    def _seed_people(person_tuples: List[CreditTuple]) -> None:
        seed_credits = SeedPersonWithCreditsBuilder(person_tuples)
        people.PeopleTable.recreate()
        people.PeopleTable.insert_people(seed_credits.people)
        movies.MoviesTable.recreate()
        movies.MoviesTable.insert_movies(seed_credits.movies)

    return _seed_people
