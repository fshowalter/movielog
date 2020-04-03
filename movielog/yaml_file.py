import abc
import os
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Type, TypeVar

import yaml

from movielog.logger import logger

TITLE_AND_YEAR_REGEX = re.compile(r"^(.*)\s\((\d{4})\)$")

T = TypeVar("T", bound="Base")  # noqa: WPS111


def represent_none(self: Any, _: Any) -> Any:
    return self.represent_scalar("tag:yaml.org,2002:null", "")


yaml.add_representer(type(None), represent_none)  # type: ignore


class YamlError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


@dataclass  # type: ignore # noqa: WPS214
class Base(abc.ABC):
    file_path: Optional[str]

    @classmethod
    @abc.abstractmethod
    def from_yaml_object(cls: Type[T], yaml_object: Dict[str, Any]) -> T:
        """ Implement behavior to hyrdate instance from a yaml object. """

    @abc.abstractmethod
    def generate_slug(self) -> str:
        """ Implement behavior to generate a slug for this instance. """

    @classmethod
    @abc.abstractmethod
    def folder_path(cls: Type[T]) -> str:
        """ Implement behavior to return the folder path for this instance. """

    @abc.abstractmethod
    def as_yaml(self) -> Dict[str, Any]:
        """
        Implement behavior to convert this instance to an object suitable for
        serializing into YAML.
        """

    @classmethod
    def from_file_path(cls: Type[T], file_path: str) -> T:
        yaml_object = None

        with open(file_path, "r") as yaml_file:
            yaml_object = yaml.safe_load(yaml_file)

        instance = cls.from_yaml_object(yaml_object)
        instance.file_path = file_path

        return instance

    def log_save(self) -> None:
        logger.log("Wrote {}", self.file_path)

    @classmethod
    def extension(cls) -> str:
        return "yml"

    def save(self, log_function: Optional[Callable[[], None]] = None) -> str:
        if not log_function:
            log_function = self.log_save

        file_path = self.file_path

        if not file_path:
            slug = self.generate_slug()
            file_path = os.path.join(
                self.__class__.folder_path(), f"{slug}.{self.__class__.extension()}"
            )
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

        with open(file_path, "wb") as output_file:
            output_file.write(
                yaml.dump(
                    self.as_yaml(),
                    encoding="utf-8",
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )
            )

        self.file_path = file_path

        log_function()

        return file_path


@dataclass  # type: ignore
class Movie(Base):
    imdb_id: str
    title: str
    year: int

    @property
    def title_with_year(self) -> str:
        return f"{self.title} ({self.year})"

    @classmethod
    def split_title_and_year(cls, title_and_year: str) -> Tuple[str, int]:
        match = TITLE_AND_YEAR_REGEX.match(title_and_year)
        if match:
            return (match.group(1), int(match.group(2)))
        raise YamlError(f"Unable to parse {title_and_year} for title and year")


@dataclass  # type: ignore
class WithSequence(Base):
    sequence: Optional[int]

    @classmethod
    @abc.abstractmethod
    def load_all(cls) -> Sequence["WithSequence"]:
        """ Implement behavior to load all instances of this class. """

    def next_sequence(self) -> int:
        existing_instances: Sequence[WithSequence] = self.__class__.load_all()
        next_sequence = len(existing_instances) + 1
        last_instance: Optional[WithSequence] = None

        if next_sequence > 1:
            last_instance = existing_instances[-1]

        if last_instance and (last_instance.sequence != (next_sequence - 1)):
            raise YamlError(
                "Last {0} ({1} has sequence {2} but next sequence is {3}".format(
                    self.__class__,
                    existing_instances[-1:],
                    last_instance.sequence,
                    next_sequence,
                ),
            )

        return next_sequence

    def save(self, log_function: Optional[Callable[[], None]] = None) -> str:
        self.sequence = self.next_sequence()
        return super().save(log_function=log_function)
