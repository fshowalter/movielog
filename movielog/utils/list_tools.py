from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from typing import Callable, TypeVar

ListType = TypeVar("ListType")


def group_list_by_key(
    iterable: Iterable[ListType], key: Callable[[ListType], str]
) -> dict[str, list[ListType]]:
    items_by_key = defaultdict(list)

    for iterable_item in iterable:
        items_by_key[key(iterable_item)].append(iterable_item)

    return items_by_key
