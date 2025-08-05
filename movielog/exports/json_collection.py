from typing import TypedDict


class JsonCollection(TypedDict):
    """Base collection metadata."""

    name: str
    slug: str
    titleCount: int
    reviewCount: int
    description: str
