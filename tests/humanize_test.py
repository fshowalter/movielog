import pytest

from movielog.internal import humanize


@pytest.mark.parametrize("test_input, expected", [(1000, "1,000"), (100, "100")])
def test_intcomma(test_input: int, expected: str) -> None:
    test_result = humanize.intcomma(test_input)

    assert test_result == expected
