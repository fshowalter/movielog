from movielog.repository.datasets import api as datasets_api
from movielog.repository.db import names_table, titles_table


def update_titles_and_names(
    titles: list[datasets_api.DatasetTitle], names: list[datasets_api.DatasetName]
) -> None:
    titles_table.reload(titles=titles)
    names_table.reload(names=names)
