import pytest

from movielog.utils import format_tools


@pytest.mark.parametrize("test_input, expected", [(1000, "1,000"), (100, "100")])
def test_humanize_int_adds_comma_when_appropriate(
    test_input: int, expected: str
) -> None:
    assert format_tools.humanize_int(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (1.678, "1.7B"),
        (106, "106.0B"),
        (3000.5, "2.9KiB"),
        (86780.0, "84.7KiB"),
        (445478.34, "435.0KiB"),
        (5866458.34, "5.6MiB"),
        (36788726.0, "35.1MiB"),
        (835488726.0, "796.8MiB"),
        (1987654852.0, "1.9GiB"),
        (325877892548668857899255685872.0, "269559.9YiB"),
    ],
)
def test_pretty_file_size_returns_humanized_sizes(
    test_input: float, expected: str
) -> None:
    assert format_tools.pretty_file_size(test_input) == expected
