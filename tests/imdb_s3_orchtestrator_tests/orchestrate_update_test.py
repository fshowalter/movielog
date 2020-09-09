from pytest_mock import MockerFixture

from movielog import imdb_s3_orchestrator


def test_calls_updates_in_correct_sequence(mocker: MockerFixture) -> None:
    manager = mocker.Mock()
    manager.attach_mock(
        mocker.patch("movielog.imdb_s3_orchestrator.movies.update"), "update_movies"
    )
    manager.attach_mock(
        mocker.patch("movielog.imdb_s3_orchestrator.people.update"), "update_people"
    )
    manager.attach_mock(
        mocker.patch("movielog.imdb_s3_orchestrator.crew_credits.update"),
        "update_crew_credits",
    )
    manager.attach_mock(
        mocker.patch("movielog.imdb_s3_orchestrator.aka_titles.update"),
        "update_aka_titles",
    )
    manager.attach_mock(
        mocker.patch("movielog.imdb_s3_orchestrator.principals.update"),
        "update_principals",
    )

    expected_calls = [
        mocker.call.update_movies(),
        mocker.call.update_people(),
        mocker.call.update_crew_credits(),
        mocker.call.update_aka_titles(),
        mocker.call.update_principals(),
    ]

    imdb_s3_orchestrator.orchestrate_update()

    assert manager.mock_calls == expected_calls
