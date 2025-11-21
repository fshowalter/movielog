from __future__ import annotations

import io
import json
from collections.abc import Iterable
from copy import deepcopy
from pathlib import Path
from typing import Any

from movielog.repository.json_watchlist_person import JsonWatchlistPerson
from movielog.utils import path_tools
from movielog.utils.logging import logger

FOLDER_NAME = "watchlist"

type UntypedJson = dict[Any, Any]


def _remove_null_fields(watchlist_person: JsonWatchlistPerson) -> UntypedJson:
    cloned_entity: UntypedJson = deepcopy(watchlist_person)  # type: ignore

    cloned_entity["titles"] = [
        {k: v for k, v in title.items() if v is not None} for title in watchlist_person["titles"]
    ]

    return cloned_entity


def serialize(
    watchlist_person: JsonWatchlistPerson,
    folder_name: str,
) -> Path:
    file_path = Path(FOLDER_NAME) / folder_name / "{}.json".format(watchlist_person["slug"])

    path_tools.ensure_file_path(file_path)

    entity_with_no_null_fields = _remove_null_fields(watchlist_person)

    with Path.open(file_path, "w", encoding="utf8") as output_file:
        output_file.write(
            json.dumps(entity_with_no_null_fields, default=str, indent=2, ensure_ascii=False)
        )

    logger.log("Wrote {}", file_path)

    return file_path


def read_all(folder_name: str) -> Iterable[io.TextIOWrapper]:
    for file_path in (Path(FOLDER_NAME) / folder_name).glob("*.json"):
        with Path.open(file_path) as json_file:
            yield json_file
