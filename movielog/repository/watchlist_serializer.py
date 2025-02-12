from __future__ import annotations

import io
import json
import os
from collections.abc import Iterable
from glob import glob
from typing import TypedDict

from movielog.utils import path_tools
from movielog.utils.logging import logger

FOLDER_NAME = "watchlist"


class WatchlistEntity(TypedDict):
    slug: str


def serialize(
    watchlist_entity: WatchlistEntity,
    folder_name: str,
) -> str:
    file_path = os.path.join(
        FOLDER_NAME,
        folder_name,
        "{0}.json".format(watchlist_entity["slug"]),
    )

    path_tools.ensure_file_path(file_path)

    with open(file_path, "w", encoding="utf8") as output_file:
        output_file.write(json.dumps(watchlist_entity, default=str, indent=2, ensure_ascii=False))

    logger.log("Wrote {}", file_path)

    return file_path


def read_all(folder_name: str) -> Iterable[io.TextIOWrapper]:
    for file_path in glob(os.path.join(FOLDER_NAME, folder_name, "*.json")):
        with open(file_path) as json_file:
            yield json_file
