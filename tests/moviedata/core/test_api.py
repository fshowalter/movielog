from pytest_mock import MockerFixture

from movielog.moviedata.core import api as core_api


def test_refresh_refreshes_all_datasets(
    mocker: MockerFixture,
) -> None:

    mocks = [
        mocker.patch("movielog.moviedata.core.api.names_dataset.refresh"),
        mocker.patch("movielog.moviedata.core.api.title_akas_dataset.refresh"),
        mocker.patch("movielog.moviedata.core.api.titles_dataset.refresh"),
    ]

    core_api.refresh()

    for mock_export in mocks:
        mock_export.assert_called_once()
