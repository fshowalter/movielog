import re
from typing import Union


def intcomma(value: Union[int, str]) -> str:  # noqa: WPS110
    # lifted from https://github.com/jmoiron/humanize/blob/master/src/humanize/number.py
    """Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'."""
    orig = str(value)
    new = re.sub(r"^(-?\d+)(\d{3})", r"\g<1>,\g<2>", orig)
    if orig == new:
        return new

    return intcomma(new)
