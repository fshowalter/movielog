from collections import defaultdict
from collections.abc import Iterable
from typing import Callable, TypeVar

T = TypeVar("T")  # noqa: WPS111


def group_list_by_key(
    iterable: Iterable[T], key: Callable[[T], str]
) -> dict[str, list[T]]:
    items_by_key = defaultdict(list)

    for iterable_item in iterable:
        items_by_key[key(iterable_item)].append(iterable_item)

    return items_by_key
