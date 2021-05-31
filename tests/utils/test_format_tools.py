import pytest

from movielog.utils import format_tools


@pytest.mark.parametrize("test_input, expected", [(1000, "1,000"), (100, "100")])
def test_humanize_int_adds_comma_when_appropriate(
    test_input: int, expected: str
) -> None:
    test_result = format_tools.humanize_int(test_input)

    assert test_result == expected
