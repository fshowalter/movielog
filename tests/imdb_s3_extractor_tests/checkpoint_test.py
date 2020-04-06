import os

from pytest_mock import MockFixture

from movielog import imdb_s3_extractor


def test_touches_success_file_when_complete(tmp_path: str) -> None:
    file_path = os.path.join(tmp_path, "imdbs3_extractor_test.tsv")
    expected = f"{file_path}._success"

    for _ in imdb_s3_extractor.checkpoint(file_path):  # noqa: WPS122, WPS328
        pass

    assert os.path.exists(expected)


def test_does_not_yield_if_success_file_found(
    tmp_path: str, mocker: MockFixture
) -> None:
    file_path = os.path.join(tmp_path, "imdbs3_extractor_test.tsv")
    open(f"{file_path}._success", "a").close()  # noqa: WPS515

    mock_action = mocker.Mock()

    for _ in imdb_s3_extractor.checkpoint(  # noqa: WPS122, WPS328, WPS352
        file_path
    ):  # pragma: no cover
        mock_action()

    mock_action.assert_not_called()
