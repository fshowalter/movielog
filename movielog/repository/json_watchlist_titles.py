from typing import TypedDict

JsonTitle = TypedDict("JsonTitle", {"imdbId": str, "title": str})


JsonExcludedTitle = TypedDict(
    "JsonExcludedTitle",
    {
        "imdbId": str,
        "title": str,
        "reason": str,
    },
)
