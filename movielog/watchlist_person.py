import abc
import os
from dataclasses import dataclass
from typing import Type, TypeVar, Union

from movielog import imdb_http, movies
from movielog.logger import logger
from movielog.watchlist_file import WATCHLIST_PATH, Title, WatchlistFile

PersonType = TypeVar("PersonType", bound="Person")  # noqa: WPS111
PersonTitle = Title


@dataclass(init=False)  # type: ignore
class Person(WatchlistFile):  # noqa: WPS214
    imdb_id: str

    @property
    @abc.abstractmethod
    def credit_key(self) -> str:
        """ Implement behavior to return the credit key for this instance. """

    @classmethod
    def refresh_all_item_titles(cls) -> None:
        for person_item in cls.unfrozen_items():
            person_item.refresh_item_titles()

    def log_save(self) -> None:
        logger.log(
            "Wrote {} ({}) to {} with {} movies",
            self.name,
            self.imdb_id,
            self.file_path,
            len(self.titles),
        )

    def refresh_item_titles(self) -> None:  # noqa: WPS231
        logger.log(
            "==== Begin refreshing {} credits for {}...", self.credit_key, self.name,
        )

        self.titles = []

        credits_for_person = imdb_http.credits_for_person(self.imdb_id, self.credit_key)

        for credit_for_person in credits_for_person:
            if credit_for_person.imdb_id not in movies.title_ids():
                self.log_skip(credit_for_person, credit_for_person.notes)
                continue
            if credit_for_person.in_production:
                self.log_skip(credit_for_person, f"({credit_for_person.in_production})")
                continue
            if credit_for_person.is_silent_film():
                self.log_skip(credit_for_person, "(silent film)")
                continue

            self.titles.append(
                Title(
                    imdb_id=credit_for_person.imdb_id,
                    title=credit_for_person.title,
                    year=credit_for_person.year,
                    notes=credit_for_person.notes,
                )
            )

        self.save()

    def log_skip(
        self, credit_for_person: imdb_http.CreditForPerson, reason: str
    ) -> None:
        logger.log(
            "Skipping {0} ({1}) for {2} {3}",
            credit_for_person.title,
            credit_for_person.year,
            self.name,
            reason,
        )


class Director(Person):
    @classmethod
    def folder_path(cls) -> str:
        return os.path.join(WATCHLIST_PATH, "directors")

    @property
    def credit_key(self) -> str:
        return "director"


class Performer(Person):
    @classmethod
    def folder_path(cls) -> str:
        return os.path.join(WATCHLIST_PATH, "performers")

    @property
    def credit_key(self) -> str:
        return "performer"


class Writer(Person):
    @classmethod
    def folder_path(cls) -> str:
        return os.path.join(WATCHLIST_PATH, "writers")

    @property
    def credit_key(self) -> str:
        return "writer"


def add(
    cls: Type[Union[Performer, Director, Writer]], imdb_id: str, name: str
) -> Person:
    watchlist_person = cls(imdb_id=imdb_id, name=name)
    watchlist_person.save()
    watchlist_person.refresh_item_titles()
    return watchlist_person
