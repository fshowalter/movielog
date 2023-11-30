import copy

from movielog.repository.data import json_titles
from movielog.repository.datasets import api as datasets_api
from movielog.utils.logging import logger


def update_for_title_datasets(titles: dict[str, datasets_api.DatasetTitle]) -> None:
    for json_title in json_titles.deserialize_all():
        dataset_title = titles.get(json_title["imdbId"], None)
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
