from typing import Callable, List

import pytest
from prompt_toolkit.application.current import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.input.posix_pipe import PosixPipeInput

from movielog import crew_credits, movies, people
from tests.cli.typehints import CreditTuple, MovieTuple


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


class SeedCreditBuilder(object):
    def __init__(self, credit_tuples: List[CreditTuple]) -> None:
        self.movies = []
        self.people = []
        self.crew_credits = []

        for credit_tuple in credit_tuples:
            person = people.Person(
                imdb_id=credit_tuple[0],
                full_name=credit_tuple[1],
                last_name=None,
                first_name=None,
                birth_year=None,
                death_year=None,
                primary_profession=None,
                known_for_title_ids="",
            )

            for movie_tuple in credit_tuple[2]:
                movie = movies.Movie(
                    imdb_id=movie_tuple[0],
                    title=movie_tuple[1],
                    original_title=movie_tuple[1],
                    year=str(movie_tuple[2]),
                    runtime_minutes="",
                    principal_cast=[],
                )

                person.known_for_title_ids = (
                    f"{person.known_for_title_ids},{movie.imdb_id}"
                )

                self.crew_credits.append(
                    crew_credits.CrewCredit(
                        movie_imdb_id=movie.imdb_id,
                        person_imdb_id=person.imdb_id,
                        sequence="1",
                    )
                )

                self.movies.append(movie)
            self.people.append(person)


@pytest.fixture
def seed_directors() -> Callable[[List[CreditTuple]], None]:
    def _seed_directors(director_tuples: List[CreditTuple]) -> None:
        seed_credits = SeedCreditBuilder(director_tuples)
        people.PeopleTable.recreate()
        people.PeopleTable.insert_people(seed_credits.people)
        movies.MoviesTable.recreate()
        movies.MoviesTable.insert_movies(seed_credits.movies)
        crew_credits.DirectingCreditsTable.recreate()
        crew_credits.DirectingCreditsTable.insert_credits(seed_credits.crew_credits)

    return _seed_directors


@pytest.fixture
def seed_writers() -> Callable[[List[CreditTuple]], None]:
    def _seed_writers(writer_tuples: List[CreditTuple]) -> None:
        seed_credits = SeedCreditBuilder(writer_tuples)
        people.PeopleTable.recreate()
        people.PeopleTable.insert_people(seed_credits.people)
        movies.MoviesTable.recreate()
        movies.MoviesTable.insert_movies(seed_credits.movies)
        crew_credits.WritingCreditsTable.recreate()
        crew_credits.WritingCreditsTable.insert_credits(seed_credits.crew_credits)

    return _seed_writers


@pytest.fixture
def seed_performers() -> Callable[[List[CreditTuple]], None]:
    def _seed_performers(writer_tuples: List[CreditTuple]) -> None:
        seed_credits = SeedCreditBuilder(writer_tuples)
        people.PeopleTable.recreate()
        people.PeopleTable.insert_people(seed_credits.people)
        movies.MoviesTable.recreate()
        movies.MoviesTable.insert_movies(seed_credits.movies)

    return _seed_performers
