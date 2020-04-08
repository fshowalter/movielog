from datetime import date

import pytest
from pytest_mock import MockFixture

from movielog import movies, people
from movielog.cli import add_viewing
from tests.cli.keys import Backspace, Down, Enter, Escape
from tests.cli.typehints import PosixPipeInput

Movie = movies.Movie
Person = people.Person
Principal = movies.Principal


@pytest.fixture(autouse=True)
def mock_viewings_add(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.add_viewing.viewings.add")


@pytest.fixture(autouse=True)
def stub_venues(mocker: MockFixture) -> MockFixture:
    venues = [
        "AFI Silver",
        "Alamo Drafthouse",
        "Blu-ray",
    ]

    return mocker.patch("movielog.cli.add_viewing.viewings.venues", return_value=venues)


@pytest.fixture(autouse=True)
def seed_db() -> None:
    seed_people = [
        Person(
            imdb_id="nm0000078",
            full_name="John Wayne",
            last_name=None,
            first_name=None,
            birth_year=None,
            death_year=None,
            primary_profession=None,
            known_for_title_ids=None,
        ),
        Person(
            imdb_id="nm0001509",
            full_name="Dean Martin",
            last_name=None,
            first_name=None,
            birth_year=None,
            death_year=None,
            primary_profession=None,
            known_for_title_ids=None,
        ),
        Person(
            imdb_id="tt0053221",
            full_name="Ricky Nelson",
            last_name=None,
            first_name=None,
            birth_year=None,
            death_year=None,
            primary_profession=None,
            known_for_title_ids=None,
        ),
    ]

    people.PeopleTable.recreate()
    people.PeopleTable.insert_people(seed_people)

    seed_movies = [
        Movie(
            imdb_id="tt0051554",
            title="Horror of Dracula",
            original_title="Dracula",
            year="1958",
            runtime_minutes="82",
            principal_cast=[
                Principal(
                    movie_imdb_id="tt0051554",
                    person_imdb_id="nm0001088",
                    sequence=1,
                    category=None,
                    job=None,
                    characters=None,
                ),
            ],
        ),
        Movie(
            imdb_id="tt0053221",
            title="Rio Bravo",
            original_title="Rio Bravo",
            year="1959",
            runtime_minutes="141",
            principal_cast=[
                Principal(
                    movie_imdb_id="tt0053221",
                    person_imdb_id="nm0000078",
                    sequence=1,
                    category=None,
                    job=None,
                    characters=None,
                ),
                Principal(
                    movie_imdb_id="tt0053221",
                    person_imdb_id="nm0001509",
                    sequence=2,
                    category=None,
                    job=None,
                    characters=None,
                ),
                Principal(
                    movie_imdb_id="tt0053221",
                    person_imdb_id="nm0625699",
                    sequence=3,
                    category=None,
                    job=None,
                    characters=None,
                ),
            ],
        ),
        Movie(
            imdb_id="tt0050280",
            title="The Curse of Frankenstein",
            original_title="The Curse of Frankenstein",
            year="1957",
            runtime_minutes="82",
            principal_cast=[
                Principal(
                    movie_imdb_id="tt0050280",
                    person_imdb_id="nm0001088",
                    sequence=1,
                    category=None,
                    job=None,
                    characters=None,
                )
            ],
        ),
        Movie(
            imdb_id="tt0089175",
            title="Fright Night",
            original_title="Fright Night",
            year="1985",
            runtime_minutes="106",
            principal_cast=[
                Principal(
                    movie_imdb_id="tt0089175",
                    person_imdb_id="nm0001697",
                    sequence=1,
                    category=None,
                    job=None,
                    characters=None,
                )
            ],
        ),
        Movie(
            imdb_id="tt0116671",
            title="Jack Frost",
            original_title="Jack Frost",
            year="1997",
            runtime_minutes="89",
            principal_cast=[
                Principal(
                    movie_imdb_id="tt0116671",
                    person_imdb_id="nm0531924",
                    sequence=1,
                    category=None,
                    job=None,
                    characters=None,
                ),
            ],
        ),
    ]
    movies.MoviesTable.recreate()
    movies.MoviesTable.insert_movies(seed_movies)


def test_calls_add_viewing(
    mock_input: PosixPipeInput, mock_viewings_add: MockFixture
) -> None:
    mock_input.send_text(
        f"Rio Bravo{Enter}{Down}{Enter}y2016-03-12{Enter}y{Down}{Down}{Enter}y"  # noqa: WPS221
    )
    add_viewing.prompt()

    mock_viewings_add.assert_called_once_with(
        imdb_id="tt0053221",
        title="Rio Bravo",
        venue="Blu-ray",
        viewing_date=date(2016, 3, 12),
        year=1959,
    )


def test_does_not_call_add_viewing_if_movie_is_none(
    mock_input: PosixPipeInput, mock_viewings_add: MockFixture
) -> None:
    mock_input.send_text(f"{Escape}")  # noqa: WPS221
    add_viewing.prompt()

    mock_viewings_add.assert_not_called()


def test_does_not_call_add_viewing_if_date_is_none(
    mock_input: PosixPipeInput, mock_viewings_add: MockFixture
) -> None:
    mock_input.send_text(
        f"Rio Bravo{Enter}{Down}{Enter}y{Escape}{Escape}"
    )  # noqa: WPS221
    add_viewing.prompt()

    mock_viewings_add.assert_not_called()


def test_guards_against_bad_dates(
    mock_input: PosixPipeInput, mock_viewings_add: MockFixture
) -> None:
    mock_input.send_text(
        f"Rio Bravo{Enter}{Down}{Enter}y2016-3-32{Enter}{Backspace}1{Enter}y{Down}{Down}{Enter}y"  # noqa: E501, WPS221
    )
    add_viewing.prompt()

    mock_viewings_add.assert_called_once_with(
        imdb_id="tt0053221",
        title="Rio Bravo",
        venue="Blu-ray",
        viewing_date=date(2016, 3, 31),
        year=1959,
    )
