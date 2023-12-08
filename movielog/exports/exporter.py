from __future__ import annotations

import json
import os
from collections.abc import Iterable
from typing import Callable, TypeVar

from movielog.utils.logging import logger

DictType = TypeVar("DictType")

EXPORT_FOLDER_NAME = "export"


def serialize_dicts(dicts: Iterable[DictType], file_name: str) -> None:
    folder_path = os.path.join(EXPORT_FOLDER_NAME)
    os.makedirs(folder_path, exist_ok=True)

    json_file_name = os.path.join(folder_path, "{0}.json".format(file_name))
    with open(json_file_name, "w") as output_file:
        output_file.write(json.dumps(dicts, default=str, indent=2))

    logger.log(
        "Wrote {} ({}).",
        json_file_name,
        pretty_file_size(os.path.getsize(json_file_name)),
    )


def serialize_dicts_to_folder(
    dicts: Iterable[DictType],
    folder_name: str,
    filename_key: Callable[[DictType], str],
) -> None:
    folder_path = os.path.join(EXPORT_FOLDER_NAME, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    for dict_to_serialize in dicts:
        file_name = os.path.join(
            folder_path, "{0}.json".format(filename_key(dict_to_serialize))
        )
        with open(file_name, "w") as output_file:
            output_file.write(json.dumps(dict_to_serialize, default=str, indent=2))
        logger.log(
            "Wrote {} ({}).",
            file_name,
            pretty_file_size(os.path.getsize(file_name)),
        )


def pretty_file_size(num: float, suffix: str = "B") -> str:
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:  # noqa: WPS459
            return "{0:.1f}{1}{2}".format(num, unit, suffix)
        num /= 1024.0
    return "{0:.1f}{1}{2}".format(num, "Yi", suffix)
