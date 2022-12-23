from movielog.utils import export_tools
from movielog.utils.logging import logger
from movielog.viewings.exports import most_watched_people


def export() -> None:
    logger.log("==== Begin exporting {}...", "most watched writers")
    stat_files = most_watched_people.generate("writing_credits", "writer_imdb_id")
    export_tools.serialize_dicts_to_folder(
        dicts=stat_files,
        folder_name="most_watched_writers",
        filename_key=lambda stats: stats["viewingYear"],
    )
