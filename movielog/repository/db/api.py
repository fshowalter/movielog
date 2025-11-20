from movielog.repository.datasets import api as datasets_api
from movielog.repository.db import db as database
from movielog.repository.db import titles_table

db = database


def update_titles(titles: list[datasets_api.DatasetTitle]) -> None:
    titles_table.reload(titles=titles)
