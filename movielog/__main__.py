import os
import re
from glob import glob

import yaml

from movielog import reviews
from movielog.internal import db

FM_REGEX = re.compile(r"^-{3,}\s*$", re.MULTILINE)


def fix_reviews() -> None:
    loaded_reviews = []

    for review_file_path in glob(os.path.join("reviews-old", "*.md")):
        with open(review_file_path, "r") as review_file:
            review_file_content = review_file.read()
        _, fm, review_content = FM_REGEX.split(review_file_content, 2)
        front_matter = yaml.safe_load(fm)

        with db.connect() as connection:
            cursor = connection.cursor()
            row = cursor.execute(
                f'SELECT title, year FROM movies WHERE imdb_id="{front_matter[":imdb_id"]}";'
            ).fetchone()
            year = row["year"]
            title = row["title"]

        loaded_reviews.append(
            {
                "imdb_id": front_matter[":imdb_id"],
                "sequence": front_matter[":sequence"],
                "title": title,
                "year": year,
                "date": front_matter[":date"],
                "content": review_content,
                "grade": front_matter[":grade"],
            }
        )

    loaded_reviews.sort(key=lambda d: d["sequence"])

    for review in loaded_reviews:
        new_review = reviews.add(
            imdb_id=review["imdb_id"],
            year=review["year"],
            title=review["title"],
            review_date=review["date"],
        )

        new_review.review_content = review["content"]
        new_review.grade = review["grade"]
        new_review.save()


if __name__ == "__main__":
    fix_reviews()
