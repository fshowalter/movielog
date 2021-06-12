from movielog.reviews.exports import most_watched_people
from movielog.utils import export_tools
from movielog.utils.logging import logger


def export() -> None:
    logger.log("==== Begin exporting {}...", "most watched performers")
    stat_files = most_watched_people.generate("performing_credits", "performer_imdb_id")
    export_tools.serialize_dataclasses_to_folder(
        dataclasses=stat_files,
        folder_name="most_watched_performers",
        filename_key=lambda stats: stats.viewing_year,
    )
