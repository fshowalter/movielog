from movielog.reviews.exports import highest_rated_people
from movielog.utils import export_tools
from movielog.utils.logging import logger


def export() -> None:
    logger.log("==== Begin exporting {}...", "highest rated writers")
    stat_files = highest_rated_people.generate("writing_credits", "writer_imdb_id")
    export_tools.serialize_dataclasses_to_folder(
        dataclasses=stat_files,
        folder_name="highest_rated_writers",
        filename_key=lambda stats: stats.review_year,
    )
