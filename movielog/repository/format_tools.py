import re
from typing import Union


def pretty_file_size(num: float, suffix: str = "B") -> str:
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:  # noqa: WPS459
            return "{0:.1f}{1}{2}".format(num, unit, suffix)
        num /= 1024.0
    return "{0:.1f}{1}{2}".format(num, "Yi", suffix)


def humanize_int(value: Union[int, str]) -> str:  # noqa: WPS110
    # lifted from https://github.com/jmoiron/humanize/blob/master/src/humanize/number.py
    """Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'."""
    orig = str(value)
    new = re.sub(r"^(-?\d+)(\d{3})", r"\g<1>,\g<2>", orig)
    if orig == new:
        return new

    return humanize_int(new)
