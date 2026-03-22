import gzip
from pathlib import Path

import pytest

from movielog.repository.datasets import extractor


@pytest.fixture
def test_file(tmp_path: Path) -> Path:
    content = (
        "tconst\taverageRating\tnumVotes\n"
        "tt0053221\t8.0\t100000\n"
        "tt0031387\tincomplete_row\n"
        "tt0089175\t7.2\t85000"
    )
    gz_path = tmp_path / "test.tsv.gz"
    with gzip.open(gz_path, "wt", encoding="utf-8") as f:
        f.write(content)
    return gz_path


def test_extractor_skips_incomplete_rows(test_file: Path) -> None:
    expected = [
        ["tt0053221", "8.0", "100000"],
        ["tt0089175", "7.2", "85000"],
    ]

    assert list(extractor.extract(test_file)) == expected
