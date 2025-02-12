from typing import TypedDict


class DatasetTitle(TypedDict):
    imdb_id: str
    title: str
    original_title: str
    year: str
    full_title: str
    runtime_minutes: int | None
    principal_cast: list[str]
    aka_titles: list[str]
    imdb_votes: int | None
    imdb_rating: float | None
