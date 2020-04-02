import os
from typing import Type, Union

import pytest
from pytest_mock import MockFixture

from movielog import watchlist_person
from movielog.watchlist_person import Director, Performer, Writer


@pytest.fixture(autouse=True)
def mock_imdb_call(mocker: MockFixture) -> None:
    mocker.patch("movielog.imdb_http.credits_for_person", return_value=[])


@pytest.mark.parametrize(
    "class_type, folder",
    [(Director, "directors"), (Performer, "performers"), (Writer, "writers")],
)
def test_saves_and_refreshes_person(
    tmp_path: str,
    mocker: MockFixture,
    class_type: Type[Union[Performer, Director, Writer]],
    folder: str,
) -> None:
    mocker.patch("movielog.watchlist_person.WATCHLIST_PATH", tmp_path)

    expected = "frozen: false\nname: Orson Welles\nimdb_id: nm0000080\ntitles: []\n"

    watchlist_person.add(cls=class_type, imdb_id="nm0000080", name="Orson Welles")

    with open(os.path.join(tmp_path, folder, "orson-welles.yml"), "r") as output_file:
        yaml_content = output_file.read()

    assert yaml_content == expected
