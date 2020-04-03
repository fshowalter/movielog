from movielog import reviews


def test_set_to_reviews() -> None:
    assert reviews.Review.folder_path() == "reviews"
