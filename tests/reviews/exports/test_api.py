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
        mocker.patch("movielog.reviews.exports.api.most_watched_directors.export"),
        mocker.patch("movielog.reviews.exports.api.most_watched_movies.export"),
        mocker.patch("movielog.reviews.exports.api.most_watched_performers.export"),
        mocker.patch("movielog.reviews.exports.api.most_watched_writers.export"),
        mocker.patch("movielog.reviews.exports.api.review_stats.export"),
        mocker.patch("movielog.reviews.exports.api.reviewed_movies.export"),
        mocker.patch("movielog.reviews.exports.api.viewing_counts_for_decades.export"),
        mocker.patch("movielog.reviews.exports.api.top_venues.export"),
        mocker.patch("movielog.reviews.exports.api.viewing_stats.export"),
        mocker.patch("movielog.reviews.exports.api.viewings.export"),
        mocker.patch("movielog.reviews.exports.api.underseen_gems.export"),
        mocker.patch("movielog.reviews.exports.api.overrated_disappointments.export"),
    ]

    exports_api.export()

    for mock_export in mocks:
        mock_export.assert_called_once()
