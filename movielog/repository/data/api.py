import copy
from dataclasses import dataclass
from typing import Iterable, Optional

from movielog.repository.data import json_metadata, json_titles
from movielog.repository.datasets import api as datasets_api
from movielog.utils.logging import logger


@dataclass
class Title(object):
    imdb_id: str
    title: str


@dataclass
class Viewing(object):
    imdb_id: str

    def title(self, cache: Optional[list[Title]] = None) -> Title:
        title_iterable = cache or titles()
        return next(title for title in title_iterable if title.imdb_id == self.imdb_id)


@dataclass
class Review(object):
    imdb_id: str
    title: str


def hydrate_json_title(json_title: json_titles.JsonTitle) -> Title:
    return Title(imdb_id=json_title["imdbId"], title=json_title["imdbId"])


def titles() -> Iterable[Title]:
    for json_title in json_titles.read_all():
        yield hydrate_json_title(json_title=json_title)


def update_for_datasets(dataset_titles: dict[str, datasets_api.DatasetTitle]) -> None:
    for json_title in json_titles.read_all():
        dataset_title = dataset_titles.get(json_title["imdbId"], None)
        if not dataset_title:
            logger.log(
                "No dataset title found for {} ({}).",
                json_title["imdbId"],
                json_title["title"],
            )
            continue

        updated_json_title = copy.deepcopy(json_title)

        updated_json_title["runtimeMinutes"] = dataset_title["runtime_minutes"]
        updated_json_title["imdbRating"] = dataset_title["imdb_rating"]
        updated_json_title["imdbVotes"] = dataset_title["imdb_votes"]

        if updated_json_title != json_title:
            json_titles.serialize(updated_json_title)

    json_metadata.update(list(dataset_titles.values()))
