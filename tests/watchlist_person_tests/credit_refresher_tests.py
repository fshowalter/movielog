from typing import List, Type, Union

import pytest
from pytest_mock import MockerFixture

from movielog import imdb_http
from movielog.watchlist_person import (
    CreditRefresher,
    Director,
    Movie,
    Performer,
    Writer,
)


@pytest.fixture
def credits_for_person(mocker: MockerFixture) -> List[imdb_http.CreditForPerson]:
    imdb_htttp_credits = [
        imdb_http.CreditForPerson(
            imdb_id="tt0053125",
            title="North by Northwest",
            year=1959,
            notes="",
            in_production="",
        ),
        imdb_http.CreditForPerson(
            imdb_id="tt9999999",
            title="North by Northwest 2",
            year=2025,
            notes="based on",
            in_production="",
        ),
        imdb_http.CreditForPerson(
            imdb_id="tt0017075",
            title="The Lodger: A Story of the London Fog",
            year=1927,
            notes="",
            in_production="",
        ),
    ]

    for imdb_htttp_credit in imdb_htttp_credits:
        mocker.patch.object(imdb_htttp_credit, "is_silent_film", return_value=False)

    return imdb_htttp_credits


@pytest.fixture(autouse=True)
def credits_for_person_mock(
    mocker: MockerFixture, credits_for_person: List[imdb_http.CreditForPerson]
) -> MockerFixture:
    return mocker.patch(
        "movielog.imdb_http.credits_for_person", return_value=credits_for_person
    )


@pytest.mark.parametrize(
    "class_type",
    [Director, Performer, Writer],
)
def test_refresh_person_credits(
    mocker: MockerFixture,
    class_type: Type[Union[Performer, Director, Writer]],
    credits_for_person: List[imdb_http.CreditForPerson],
    credits_for_person_mock: MockerFixture,
) -> None:
    expected = [
        Movie(imdb_id="tt0053125", title="North by Northwest", year=1959, notes=""),
        Movie(
            imdb_id="tt9999999",
            title="North by Northwest 2",
            year=2025,
            notes="based on",
        ),
        Movie(
            imdb_id="tt0017075",
            title="The Lodger: A Story of the London Fog",
            year=1927,
            notes="",
        ),
    ]

    person = class_type(file_path=None, name="Alfred Hitchcock", imdb_id="nm0000033")

    valid_movie_ids = set(["tt0053125", "tt9999999", "tt0017075"])

    mocker.patch(
        "movielog.watchlist_person.movies.title_ids", return_value=valid_movie_ids
    )

    save_mock = mocker.patch.object(person, "save")

    CreditRefresher.refresh_person_credits(person=person)

    assert person.movies == expected

    save_mock.assert_called_once()


@pytest.mark.parametrize(
    "class_type",
    [Director, Performer, Writer],
)
def test_skips_invalid_titles(
    mocker: MockerFixture,
    class_type: Type[Union[Performer, Director, Writer]],
    credits_for_person: List[imdb_http.CreditForPerson],
    credits_for_person_mock: MockerFixture,
) -> None:
    expected = [
        Movie(imdb_id="tt0053125", title="North by Northwest", year=1959, notes=""),
        Movie(
            imdb_id="tt0017075",
            title="The Lodger: A Story of the London Fog",
            year=1927,
            notes="",
        ),
    ]

    person = class_type(file_path=None, name="Alfred Hitchcock", imdb_id="nm0000033")

    valid_movie_ids = set(["tt0053125", "tt0017075"])

    mocker.patch(
        "movielog.watchlist_person.movies.title_ids", return_value=valid_movie_ids
    )

    save_mock = mocker.patch.object(person, "save")

    CreditRefresher.refresh_person_credits(person=person)

    assert person.movies == expected

    save_mock.assert_called_once()


@pytest.mark.parametrize(
    "class_type",
    [Director, Performer, Writer],
)
def test_skips_silent_movies(
    mocker: MockerFixture,
    class_type: Type[Union[Performer, Director, Writer]],
    credits_for_person: List[imdb_http.CreditForPerson],
    credits_for_person_mock: MockerFixture,
) -> None:
    expected = [
        Movie(imdb_id="tt0053125", title="North by Northwest", year=1959, notes=""),
        Movie(
            imdb_id="tt9999999",
            title="North by Northwest 2",
            year=2025,
            notes="based on",
        ),
    ]

    mocker.patch.object(credits_for_person[2], "is_silent_film", return_value=True)

    person = class_type(file_path=None, name="Alfred Hitchcock", imdb_id="nm0000033")

    valid_movie_ids = set(["tt0053125", "tt9999999", "tt0017075"])

    mocker.patch(
        "movielog.watchlist_person.movies.title_ids", return_value=valid_movie_ids
    )

    save_mock = mocker.patch.object(person, "save")

    CreditRefresher.refresh_person_credits(person=person)

    assert person.movies == expected

    save_mock.assert_called_once()


@pytest.mark.parametrize(
    "class_type",
    [Director, Performer, Writer],
)
def test_skips_in_production_titles(
    mocker: MockerFixture,
    class_type: Type[Union[Performer, Director, Writer]],
    credits_for_person: List[imdb_http.CreditForPerson],
    credits_for_person_mock: MockerFixture,
) -> None:
    expected = [
        Movie(imdb_id="tt0053125", title="North by Northwest", year=1959, notes=""),
        Movie(
            imdb_id="tt0017075",
            title="The Lodger: A Story of the London Fog",
            year=1927,
            notes="",
        ),
    ]

    credits_for_person[1].in_production = "in-development"

    person = class_type(file_path=None, name="Alfred Hitchcock", imdb_id="nm0000033")

    valid_movie_ids = set(["tt0053125", "tt9999999", "tt0017075"])

    mocker.patch(
        "movielog.watchlist_person.movies.title_ids", return_value=valid_movie_ids
    )

    save_mock = mocker.patch.object(person, "save")

    CreditRefresher.refresh_person_credits(person=person)

    assert person.movies == expected

    save_mock.assert_called_once()
