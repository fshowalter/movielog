from __future__ import annotations

import json
import os
from collections.abc import Iterable
from dataclasses import asdict
from typing import TYPE_CHECKING, Callable, TypeVar

if TYPE_CHECKING:
    from _typeshed import DataclassInstance  # noqa: WPS436

from movielog.utils import list_tools
from movielog.utils.logging import logger

DictType = TypeVar("DictType")

EXPORT_FOLDER_NAME = "exports"


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


def serialize_dicts_by_key(
    dicts: Iterable[DictType], folder_name: str, key: Callable[[DictType], str]
) -> None:
    dicts_by_key = list_tools.group_list_by_key(dicts, key=key)

    folder_path = os.path.join(EXPORT_FOLDER_NAME, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    for file_name, dicts_for_file in dicts_by_key.items():
        json_file_name = os.path.join(folder_path, "{0}.json".format(file_name))
        with open(json_file_name, "w") as output_file:
            output_file.write(json.dumps(dicts_for_file, default=str, indent=2))

        logger.log(
            "Wrote {} ({}).",
            json_file_name,
            pretty_file_size(os.path.getsize(json_file_name)),
        )


def serialize_dataclasses_to_folder(
    dataclasses: Iterable[DataclassInstance],
    folder_name: str,
    filename_key: Callable[[DataclassInstance], str],
) -> None:
    folder_path = os.path.join(EXPORT_FOLDER_NAME, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    for dataclass in dataclasses:
        file_name = os.path.join(
            folder_path, "{0}.json".format(filename_key(dataclass))
        )
        with open(file_name, "w") as output_file:
            output_file.write(json.dumps(asdict(dataclass), default=str, indent=2))
        logger.log(
            "Wrote {} ({}).",
            file_name,
            pretty_file_size(os.path.getsize(file_name)),
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
