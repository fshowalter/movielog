import pytest
from prompt_toolkit.application.current import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.input.posix_pipe import PosixPipeInput
from pytest_mock import MockFixture


@pytest.fixture(autouse=True, scope="function")
def mock_input(mocker: MockFixture) -> PosixPipeInput:
    pipe_input = create_pipe_input()
    with create_app_session(input=pipe_input):
        yield pipe_input
