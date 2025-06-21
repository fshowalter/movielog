from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from pathlib import Path

from movielog.utils.logging import logger

EXPORT_FOLDER_NAME = "export"


def serialize_dict[T](dict_to_export: T, file_name: str) -> None:
    folder_path = Path(EXPORT_FOLDER_NAME)
    folder_path.mkdir(exist_ok=True, parents=True)

    json_file_name = folder_path / f"{file_name}.json"
    with Path.open(json_file_name, "w") as output_file:
        output_file.write(json.dumps(dict_to_export, default=str, indent=2))

    logger.log(
        "Wrote {} ({}).",
        json_file_name,
        pretty_file_size(json_file_name.stat().st_size),
    )


def serialize_dicts[T](dicts: Iterable[T], file_name: str) -> None:
    folder_path = Path(EXPORT_FOLDER_NAME)
    folder_path.mkdir(exist_ok=True, parents=True)

    json_file_name = folder_path / f"{file_name}.json"
    with Path.open(json_file_name, "w") as output_file:
        output_file.write(json.dumps(dicts, default=str, indent=2))

    logger.log(
        "Wrote {} ({}).",
        json_file_name,
        pretty_file_size(json_file_name.stat().st_size),
    )


def serialize_dicts_to_folder[T](
    dicts: Iterable[T],
    folder_name: str,
    filename_key: Callable[[T], str],
) -> None:
    folder_path = Path(EXPORT_FOLDER_NAME) / folder_name
    folder_path.mkdir(exist_ok=True, parents=True)

    for dict_to_serialize in dicts:
        file_name = folder_path / f"{filename_key(dict_to_serialize)}.json"
        with Path.open(file_name, "w") as output_file:
            output_file.write(json.dumps(dict_to_serialize, default=str, indent=2))
        logger.log(
            "Wrote {} ({}).",
            file_name,
            pretty_file_size(file_name.stat().st_size),
        )


def pretty_file_size(num: float, suffix: str = "B") -> str:
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:.1f}{unit}{suffix}"
        num /= 1024.0
    return "{:.1f}{}{}".format(num, "Yi", suffix)
