from movielog.utils import export_tools
from movielog.utils.logging import logger
from movielog.viewings.exports import most_watched_people


def export() -> None:
    logger.log("==== Begin exporting {}...", "most watched performers")
    stat_files = most_watched_people.generate("performing_credits", "performer_imdb_id")
    export_tools.serialize_dicts_to_folder(
        dicts=stat_files,
        folder_name="most_watched_performers",
        filename_key=lambda stats: stats["viewingYear"],
    )
