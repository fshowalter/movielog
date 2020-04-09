from typing import Callable, List

import pytest
from prompt_toolkit.application.current import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.input.posix_pipe import PosixPipeInput

from movielog import movies, people
from tests.cli.typehints import MovieTuple


@pytest.fixture(autouse=True, scope="function")
def mock_input() -> PosixPipeInput:
    pipe_input = create_pipe_input()
    with create_app_session(input=pipe_input):
        yield pipe_input
    pipe_input.close()


class SeedMovieBuilder(object):
    def __init__(self, movie_tuples: List[MovieTuple]) -> None:
        self.movies: List[movies.Movie] = []
        self.people: List[people.Person] = []

        for movie_tuple in movie_tuples:
            movie = movies.Movie(
                imdb_id=movie_tuple[0],
                title=movie_tuple[1],
                original_title=movie_tuple[1],
                year=str(movie_tuple[2]),
                runtime_minutes="",
                principal_cast=[],
            )

            for index, person in enumerate(movie_tuple[3]):
                if not any(person[0] == existing.imdb_id for existing in self.people):
                    self.people.append(
                        people.Person(
                            imdb_id=person[0],
                            full_name=person[1],
                            last_name=None,
                            first_name=None,
                            birth_year=None,
                            death_year=None,
                            primary_profession=None,
                            known_for_title_ids=None,
                        )
                    )

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
