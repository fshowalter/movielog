from pytest_mock import MockerFixture

from movielog.viewings.exports import api as exports_api


def test_export_calls_all_exports(
    mocker: MockerFixture,
) -> None:

    mocks = [
        mocker.patch("movielog.viewings.exports.api.most_watched_directors.export"),
        mocker.patch("movielog.viewings.exports.api.most_watched_movies.export"),
        mocker.patch("movielog.viewings.exports.api.most_watched_performers.export"),
        mocker.patch("movielog.viewings.exports.api.most_watched_writers.export"),
        mocker.patch("movielog.viewings.exports.api.viewing_counts_for_decades.export"),
        mocker.patch("movielog.viewings.exports.api.top_media.export"),
        mocker.patch("movielog.viewings.exports.api.viewing_stats.export"),
        mocker.patch("movielog.viewings.exports.api.viewings.export"),
    ]

    exports_api.export()

    for mock_export in mocks:
        mock_export.assert_called_once()
