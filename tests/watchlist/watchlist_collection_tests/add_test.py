import json
import os

from pytest_mock import MockerFixture

from movielog import watchlist_collection


def test_creates_new_collection(tmp_path: str, mocker: MockerFixture) -> None:
    mocker.patch("movielog.watchlist_collection.FOLDER_PATH", tmp_path)

    expected = {
        "name": "Halloween",
        "slug": "halloween",
        "movies": [],
    }

    watchlist_collection.add(name="Halloween")

    with open(os.path.join(tmp_path, "halloween.json"), "r") as output_file:
        file_content = json.load(output_file)

    assert file_content == expected
