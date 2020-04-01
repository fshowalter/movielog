import operator
import os
from dataclasses import dataclass
from typing import Sequence

from movielog.logger import logger
from movielog.watchlist_file import WATCHLIST_PATH, YEAR, Title, WatchlistFile


@dataclass(init=False)
class Collection(WatchlistFile):
    @classmethod
    def folder_path(cls) -> str:
        return os.path.join(WATCHLIST_PATH, "collections")

    def add_title(self, imdb_id: str, title: str, year: int) -> Sequence[Title]:
        self.titles.append(Title(imdb_id=imdb_id, title=title, year=year))

        self.titles.sort(key=operator.attrgetter(YEAR))

        return self.titles

    def log_save(self) -> None:
        logger.log(
            "Wrote {} to {} with {} movies",
            self.name,
            self.file_path,
            len(self.titles),
        )


def all_items() -> Sequence[Collection]:
    return Collection.all_items()


def add_collection(name: str) -> Collection:
    collection_watchlist_item = Collection(name=name)
    collection_watchlist_item.save()
    return collection_watchlist_item


def update_collection(collection: Collection) -> Collection:
    collection.save()
    return collection
