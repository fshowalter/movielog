import json
from typing import TypedDict

from movielog import db
from movielog.repository.datasets.dataset_name import DatasetName

TABLE_NAME = "names"


CREATE_DDL = """
  "imdb_id" TEXT PRIMARY KEY NOT NULL,
  "full_name" varchar(255) NOT NULL,
  "known_for_titles" JSON
"""


INSERT_DDL = """
  INSERT INTO {0}(
      imdb_id,
      full_name,
      known_for_titles)
  VALUES(
      :imdb_id,
      :full_name,
      :known_for_titles)
"""


class Row(TypedDict):
    imdb_id: str
    full_name: str
    known_for_titles: str


def reload(names: list[DatasetName]) -> None:
    db.recreate_table(TABLE_NAME, CREATE_DDL)

    db.insert_into_table(
        table_name=TABLE_NAME,
        insert_ddl=INSERT_DDL.format(TABLE_NAME),
        rows=[
            Row(
                imdb_id=name["imdb_id"],
                full_name=name["full_name"],
                known_for_titles=json.dumps(name["known_for_titles"]),
            )
            for name in names
        ],
    )

    db.add_index(TABLE_NAME, "full_name")

    db.validate_row_count(TABLE_NAME, len(names))
