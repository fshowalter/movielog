from pytest_mock import MockerFixture

from movielog.reviews.exports import api as exports_api


def test_export_calls_all_exports(
    mocker: MockerFixture,
) -> None:

    mocks = [
        mocker.patch("movielog.reviews.exports.api.average_grade_for_decades.export"),
        mocker.patch("movielog.reviews.exports.api.grade_distributions.export"),
        mocker.patch("movielog.reviews.exports.api.highest_rated_directors.export"),
        mocker.patch("movielog.reviews.exports.api.highest_rated_performers.export"),
        mocker.patch("movielog.reviews.exports.api.highest_rated_writers.export"),
        mocker.patch("movielog.reviews.exports.api.review_stats.export"),
        mocker.patch("movielog.reviews.exports.api.reviewed_movies.export"),
    ]

    exports_api.export()

    for mock_export in mocks:
        mock_export.assert_called_once()
