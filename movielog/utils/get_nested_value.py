from typing import Any


def get_nested_value(dict_obj: dict[Any, Any], keys: list[str], default: Any = None) -> Any:
    """Safely get nested dictionary values."""
    current = dict_obj
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        else:
            return default
    return current
