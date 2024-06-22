import json
import os
from collections import defaultdict
from glob import glob
from typing import Optional, cast

import yaml

from movielog.repository import markdown_reviews, markdown_viewings


def convert_viewings_to_yaml() -> None:
    viewing_notes: dict[int, Optional[str]] = defaultdict(lambda: None)

    for viewing_notes_file_path in glob(os.path.join("viewing_notes", "*.md")):
        with open(viewing_notes_file_path, "r") as viewing_notes_file:
            _, frontmatter, notes = markdown_reviews.FM_REGEX.split(
                viewing_notes_file.read(), 2
            )
            sequence = cast(int, yaml.safe_load(frontmatter)["sequence"])

            viewing_notes[sequence] = notes

    for file_path in glob(os.path.join(markdown_viewings.FOLDER_NAME, "*.json")):
        with open(file_path, "r") as json_file:
            json_viewing = cast(markdown_viewings.MarkdownViewing, json.load(json_file))
            markdown_file_path = file_path.replace(".json", ".md")

            print(json_viewing["sequence"])
            viewing_notes_content = viewing_notes[json_viewing["sequence"]] or ""
            with open(markdown_file_path, "w") as markdown_file:
                markdown_file.write("---\n")
                yaml.dump(
                    json_viewing,
                    encoding="utf-8",
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                    stream=markdown_file,
                )
                markdown_file.write("---\n\n")
                markdown_file.write(viewing_notes_content)


if __name__ == "__main__":
    convert_viewings_to_yaml()
