from movielog.utils import export_tools
from movielog.utils.logging import logger
from movielog.viewings.exports import most_watched_people


def export() -> None:
    logger.log("==== Begin exporting {}...", "most watched directors")
    stat_files = most_watched_people.generate("directing_credits", "director_imdb_id")
    export_tools.serialize_dataclasses_to_folder(
        dataclasses=stat_files,
        folder_name="most_watched_directors",
        filename_key=lambda stats: stats.viewing_year,
    )
