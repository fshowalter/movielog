from pytest_mock import MockerFixture

from movielog.moviedata.extended.tables import api as tables_api


def test_reload_calls_udpate_on_all_tables(
    mocker: MockerFixture,
) -> None:

    mocks = [
        mocker.patch("movielog.moviedata.extended.tables.countries_table.update"),
        mocker.patch(
            "movielog.moviedata.extended.tables.directing_credits_table.update"
        ),
        mocker.patch(
            "movielog.moviedata.extended.tables.performing_credits_table.update"
        ),
        mocker.patch("movielog.moviedata.extended.tables.release_dates_table.update"),
        mocker.patch("movielog.moviedata.extended.tables.sort_titles_table.update"),
        mocker.patch("movielog.moviedata.extended.tables.writing_credits_table.update"),
    ]

    tables_api.reload([])

    for mock_export in mocks:
        mock_export.assert_called_once()
