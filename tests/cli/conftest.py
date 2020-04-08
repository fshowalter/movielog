from typing import Callable, List

import pytest
from prompt_toolkit.application.current import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.input.posix_pipe import PosixPipeInput
from pytest_mock import MockFixture

from movielog import movies, people
from tests.cli.typehints import MovieTuple


@pytest.fixture(autouse=True, scope="function")
def mock_input(mocker: MockFixture) -> PosixPipeInput:
    pipe_input = create_pipe_input()
    with create_app_session(input=pipe_input):
        yield pipe_input


@pytest.fixture
def seed_movies() -> Callable[[List[MovieTuple]], None]:
    def _seed_movies(movie_tuples: List[MovieTuple]) -> None:
        movies_to_load: List[movies.Movie] = []
        people_to_load: List[people.Person] = []

        for movie_tuple in movie_tuples:
            movies_to_load.append(
                movies.Movie(
                    imdb_id=movie_tuple[0],
                    title=movie_tuple[1],
                    original_title=movie_tuple[1],
                    year=str(movie_tuple[2]),
                    runtime_minutes="",
                    principal_cast=[],
                )
            )

            for index, person in enumerate(movie_tuple[3]):
                if not any(
                    person[0] == existing.imdb_id for existing in people_to_load
                ):
                    people_to_load.append(
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

                movies_to_load[-1].principal_cast.append(
                    movies.Principal(
                        movie_imdb_id=movie_tuple[0],
                        person_imdb_id=person[0],
                        sequence=index,
                        category=None,
                        job=None,
                        characters=None,
                    )
                )

        people.PeopleTable.recreate()
        people.PeopleTable.insert_people(people_to_load)
        movies.MoviesTable.recreate()
        movies.MoviesTable.insert_movies(movies_to_load)

    return _seed_movies
