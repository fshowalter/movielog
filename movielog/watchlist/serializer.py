from __future__ import annotations

import json
import os
from dataclasses import asdict
from glob import glob
from typing import TYPE_CHECKING, Callable, Sequence, TypeVar, Union

from movielog.utils import format_tools, path_tools
from movielog.utils.logging import logger

if TYPE_CHECKING:
    from movielog.watchlist.collections import Collection
    from movielog.watchlist.directors import Director
    from movielog.watchlist.performers import Performer
    from movielog.watchlist.writers import Writer

FOLDER_PATH = "watchlist"

if TYPE_CHECKING:
    WatchlistEntityType = Union[Director, Performer, Writer, Collection]
    WatchlistEntityTypeVar = TypeVar(
        "WatchlistEntityTypeVar", Director, Performer, Writer, Collection
    )


def serialize(
    watchlist_entity: WatchlistEntityType,
    folder_name: str,
) -> str:
    #     if watchlist_entity.__class__.__name__ != "Collection":
    #         toml_file_path = os.path.join(
    #             FOLDER_PATH,
    #             watchlist_entity.folder_name,
    #             "{0}.toml".format(watchlist_entity.slug),
    #         )

    #         path_tools.ensure_file_path(toml_file_path)

    #         toml_template = """
    # name = "{0}"
    # slug = "{1}"
    # imdb_id = "{2}"
    # excluded_titles = []
    # """

    #         with open(toml_file_path, "w") as toml_output_file:
    #             toml_output_file.write(
    #                 toml_template.format(
    #                     watchlist_entity.name,
    #                     watchlist_entity.slug,
    #                     watchlist_entity.imdb_id,
    #                 ).strip()
    #             )

    file_path = os.path.join(
        FOLDER_PATH,
        folder_name,
        "{0}.json".format(watchlist_entity.slug),
    )

    path_tools.ensure_file_path(file_path)

    with open(file_path, "w") as output_file:
        output_file.write(json.dumps(asdict(watchlist_entity), default=str, indent=2))

    logger.log("Wrote {}", file_path)

    return file_path


def deserialize_all(
    folder_name: str, callback: Callable[[str], WatchlistEntityTypeVar]
) -> Sequence[WatchlistEntityTypeVar]:
    logger.log(
        "==== Begin reading {} from disk...", "watchlist {0}".format(folder_name)
    )

    file_paths = glob(os.path.join(FOLDER_PATH, folder_name, "*.json"))

    entities = [callback(file_path) for file_path in sorted(file_paths)]

    logger.log(
        "Read {} {}.",
        format_tools.humanize_int(len(entities)),
        "watchlist {0}".format(folder_name),
    )

    return entities
