import os

from pytest_mock import MockerFixture

from movielog import watchlist_collection


def test_creates_new_collection(tmp_path: str, mocker: MockerFixture) -> None:
    mocker.patch("movielog.watchlist_collection.WATCHLIST_PATH", tmp_path)

    expected = "frozen: false\nname: Halloween\nslug: halloween\ntitles: []\n"

    watchlist_collection.add(name="Halloween")

    with open(
        os.path.join(tmp_path, "collections", "halloween.yml"), "r"
    ) as output_file:
        yaml_content = output_file.read()

    assert yaml_content == expected
