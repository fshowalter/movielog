from movielog.reviews.exports import highest_rated_people
from movielog.utils import export_tools
from movielog.utils.logging import logger


def export() -> None:
    logger.log("==== Begin exporting {}...", "highest rated performers")
    stat_files = highest_rated_people.generate(
        "performing_credits", "performer_imdb_id"
    )
    export_tools.serialize_dataclasses_to_folder(
        dataclasses=stat_files,
        folder_name="highest_rated_performers",
        filename_key=lambda stats: stats.review_year,
    )
