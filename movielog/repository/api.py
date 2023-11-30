from movielog.repository.data import api as data_api
from movielog.repository.datasets import api as datasets_api
from movielog.repository.db import api as db_api


def update_datasets() -> None:
    (titles, names) = datasets_api.download_and_extract()

    db_api.update_titles_and_names(
        titles=list(titles.values()), names=list(names.values())
    )

    data_api.update_for_datasets(titles=titles)
