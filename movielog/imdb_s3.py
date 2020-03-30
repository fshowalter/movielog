from movielog import aka_titles, crew_credits, movies, people, principals
from movielog.logger import logger


@logger.catch
def orchestrate_update() -> None:
    movies.update()
    people.update()
    crew_credits.update()
    aka_titles.update()
    principals.update()
