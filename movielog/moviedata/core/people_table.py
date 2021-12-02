from typing import Optional, Sequence, TypedDict

from movielog import db

TABLE_NAME = "people"


CREATE_DDL = """
  "imdb_id" TEXT PRIMARY KEY NOT NULL,
  "full_name" varchar(255) NOT NULL,
  "known_for_title_ids" TEXT
"""


INSERT_DDL = """
  INSERT INTO {0}(
      imdb_id,
      full_name,
      known_for_title_ids)
  VALUES(
      :imdb_id,
      :full_name,
      :known_for_title_ids)
"""


class Row(TypedDict):
    imdb_id: str
    full_name: str
    known_for_title_ids: Optional[str]


def reload(rows: Sequence[Row]) -> None:
    db.recreate_table(TABLE_NAME, CREATE_DDL)

    db.insert_into_table(
        table_name=TABLE_NAME,
        insert_ddl=INSERT_DDL.format(TABLE_NAME),
        rows=rows,
    )

    db.add_index(TABLE_NAME, "full_name")

    db.validate_row_count(TABLE_NAME, len(rows))
