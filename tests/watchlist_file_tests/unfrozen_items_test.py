import os
from typing import Callable

from pytest_mock import MockerFixture

from movielog.watchlist_file import WatchlistFile


def test_returns_instance_for_each_file_where_frozen_is_false(  # noqa: WPS210
    mocker: MockerFixture,
    tmp_path: str,
    build_watchlist_file: Callable[..., WatchlistFile],
) -> None:
    expected = [
        build_watchlist_file(
            file_path=os.path.join(tmp_path, "3.yml"),
            name="David Cronenberg",
            frozen=False,
            imdb_id="nm0000343",
        ),
        build_watchlist_file(
            file_path=os.path.join(tmp_path, "4.yml"),
            name="Bill Murray",
            frozen=False,
            imdb_id="nm0000195",
        ),
    ]

    concrete_watchlist_file_class = expected[0].__class__

    mocker.patch.object(
        concrete_watchlist_file_class, "folder_path", return_value=tmp_path
    )

    with open(str(os.path.join(tmp_path, "1.yml")), "w") as output_file1:
        output_file1.write(
            """
            frozen: true
            name: Peter Cushing
            imdb_id: nm0001088
            """
        )

    with open(str(os.path.join(tmp_path, "2.yml")), "w") as output_file2:
        output_file2.write(
            """
            frozen: true
            name: Christopher Lee
            imdb_id: nm0000489
            """
        )

    with open(str(expected[0].file_path), "w") as output_file3:
        output_file3.write(
            """
            frozen: false
            name: David Cronenberg
            imdb_id: nm0000343
            """
        )

    with open(str(expected[1].file_path), "w") as output_file4:
        output_file4.write(
            """
            frozen: false
            name: Bill Murray
            imdb_id: nm0000195
            """
        )

    assert expected == list(concrete_watchlist_file_class.unfrozen_items())
