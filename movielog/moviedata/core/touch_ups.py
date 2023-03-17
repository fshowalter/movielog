from movielog import db


def apply() -> None:
    ddl = """
        UPDATE movies
        SET
            year=1988,
            title="Blood Delirium"
        WHERE imdb_id="tt0094762"
    """

    db.execute_script(ddl)
