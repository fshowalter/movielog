from pytest_mock import MockerFixture

from movielog.watchlist.exports import api as exports_api


def test_export_calls_all_exports(
    mocker: MockerFixture,
) -> None:

    mocks = [
        mocker.patch("movielog.watchlist.exports.api.watchlist_entities.export"),
        mocker.patch("movielog.watchlist.exports.api.watchlist_movies.export"),
    ]

    exports_api.export()

    for mock_export in mocks:
        mock_export.assert_called_once()
