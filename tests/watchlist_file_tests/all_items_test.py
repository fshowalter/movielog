import os
from typing import Callable

from pytest_mock import MockerFixture

from movielog.watchlist_file import WatchlistFile


def test_returns_instance_for_each_file(
    mocker: MockerFixture,
    tmp_path: str,
    build_watchlist_file: Callable[..., WatchlistFile],
) -> None:
    expected = [
        build_watchlist_file(
            file_path=os.path.join(tmp_path, "1.yml"),
            name="Peter Cushing",
            frozen=True,
            imdb_id="nm0001088",
        ),
        build_watchlist_file(
            file_path=os.path.join(tmp_path, "2.yml"),
            name="Christopher Lee",
            frozen=True,
            imdb_id="nm0000489",
        ),
    ]

    concrete_watchlist_file_class = expected[0].__class__

    mocker.patch.object(
        concrete_watchlist_file_class, "folder_path", return_value=tmp_path
    )

    with open(str(expected[0].file_path), "w") as output_file1:
        output_file1.write(
            """
            frozen: true
            name: Peter Cushing
            imdb_id: nm0001088
            """
        )

    with open(str(expected[1].file_path), "w") as output_file2:
        output_file2.write(
            """
            frozen: true
            name: Christopher Lee
            imdb_id: nm0000489
            """
        )

    assert expected == concrete_watchlist_file_class.all_items()
