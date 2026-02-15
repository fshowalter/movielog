from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable


def group_list_by_key[ListType, KeyType](
    iterable: Iterable[ListType], key: Callable[[ListType], KeyType]
) -> dict[KeyType, list[ListType]]:
    items_by_key = defaultdict(list)

    for iterable_item in iterable:
        items_by_key[key(iterable_item)].append(iterable_item)

    return items_by_key


def list_to_dict[ListType, KeyType](
    iterable: Iterable[ListType], key: Callable[[ListType], KeyType]
) -> dict[KeyType, ListType]:
    items_by_key: dict[KeyType, ListType] = {}

    for iterable_item in iterable:
        items_by_key[key(iterable_item)] = iterable_item

    return items_by_key
