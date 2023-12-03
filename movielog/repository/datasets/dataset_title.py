from typing import Optional, TypedDict


class DatasetTitle(TypedDict):
    imdb_id: str
    title: str
    original_title: str
    year: str
    full_title: str
    runtime_minutes: Optional[int]
    principal_cast: list[str]
    aka_titles: list[str]
    imdb_votes: Optional[int]
    imdb_rating: Optional[float]
