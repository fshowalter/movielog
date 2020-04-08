import pytest
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.input.posix_pipe import PosixPipeInput
from pytest_mock import MockFixture


@pytest.fixture(autouse=True)
def mock_input(mocker: MockFixture) -> PosixPipeInput:
    pipe_input = create_pipe_input()

    mocker.patch("prompt_toolkit.input.defaults.create_input", return_value=pipe_input)
    return pipe_input
