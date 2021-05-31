from __future__ import annotations

from typing import Callable, Generator, Sequence

import pytest
from prompt_toolkit.application.current import create_app_session
from prompt_toolkit.input import create_pipe_input

MockInput = Callable[[Sequence[str]], None]


@pytest.fixture(autouse=True, scope="function")
def mock_input() -> Generator[MockInput, None, None]:
    pipe_input = create_pipe_input()

    def factory(input_sequence: Sequence[str]) -> None:
        pipe_input.send_text("".join(input_sequence))

    with create_app_session(input=pipe_input):
        yield factory

    pipe_input.close()
