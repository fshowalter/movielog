from movielog import db


def apply() -> None:
    ddl = """
        UPDATE movies
        SET
            year=1988,
            title="Blood Delirium"
        WHERE imdb_id="tt0094762";

        UPDATE movies
        SET
            title="20,000 Years in Sing Sing"
        WHERE imdb_id="tt0023731";
    """

    db.execute_script(ddl)
