from typing import TypedDict


class DatasetName(TypedDict):
    imdb_id: str
    full_name: str
    known_for_titles: list[str]
