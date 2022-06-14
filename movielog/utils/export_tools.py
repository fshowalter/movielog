import json
import os
from collections.abc import Iterable
from dataclasses import asdict
from typing import Callable, TypeVar

from movielog.utils import format_tools
from movielog.utils.logging import logger

DataClassType = TypeVar("DataClassType")
DictType = TypeVar("DictType")

EXPORT_FOLDER_NAME = "export"


def serialize_dicts(dicts: Iterable[DictType], file_name: str) -> None:
    folder_path = os.path.join(EXPORT_FOLDER_NAME)
    os.makedirs(folder_path, exist_ok=True)

    json_file_name = os.path.join(folder_path, "{0}.json".format(file_name))
    with open(json_file_name, "w") as output_file:
        output_file.write(json.dumps(dicts, default=str, indent=""))

    logger.log(
        "Wrote {} ({}).",
        json_file_name,
        format_tools.pretty_file_size(os.path.getsize(json_file_name)),
    )


def serialize_dataclasses_to_folder(
    dataclasses: Iterable[DataClassType],
    folder_name: str,
    filename_key: Callable[[DataClassType], str],
) -> None:
    folder_path = os.path.join(EXPORT_FOLDER_NAME, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    for dataclass in dataclasses:
        file_name = os.path.join(
            folder_path, "{0}.json".format(filename_key(dataclass))
        )
        with open(file_name, "w") as output_file:
            output_file.write(json.dumps(asdict(dataclass), default=str, indent=""))
        logger.log(
            "Wrote {} ({}).",
            file_name,
            format_tools.pretty_file_size(os.path.getsize(file_name)),
        )
