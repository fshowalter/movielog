from pytest_mock import MockerFixture

from movielog.reviews.exports import api as exports_api


def test_export_calls_all_exports(
    mocker: MockerFixture,
) -> None:

    mocks = [
        mocker.patch("movielog.reviews.exports.api.grade_distributions.export"),
        mocker.patch("movielog.reviews.exports.api.review_stats.export"),
        mocker.patch("movielog.reviews.exports.api.reviewed_movies.export"),
        mocker.patch("movielog.reviews.exports.api.underseen_gems.export"),
        mocker.patch("movielog.reviews.exports.api.overrated_disappointments.export"),
    ]

    exports_api.export()

    for mock_export in mocks:
        mock_export.assert_called_once()
