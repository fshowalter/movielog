from movielog import aka_titles, movies, people, principals
from movielog.logger import logger


@logger.catch
def orchestrate_update() -> None:
    movies.update()
    people.update()
    aka_titles.update()
    principals.update()
