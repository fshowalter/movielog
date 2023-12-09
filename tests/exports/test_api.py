import json
import os
from pathlib import Path

import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension

from movielog.exports import api as exports_api


@pytest.fixture
def snapshot_json(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    return snapshot.with_defaults(extension_class=JSONSnapshotExtension)


def test_exports_viewings(tmp_path: Path, snapshot_json: SnapshotAssertion) -> None:
    exports_api.export_data()

    with open(
        os.path.join(tmp_path / "export", "viewings.json"),
        "r",
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == snapshot_json


def test_exports_watchlist_titles(
    tmp_path: Path, snapshot_json: SnapshotAssertion
) -> None:
    exports_api.export_data()

    with open(
        os.path.join(tmp_path / "export", "watchlist-titles.json"),
        "r",
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == snapshot_json


def test_exports_watchlist_collections(
    tmp_path: Path, snapshot_json: SnapshotAssertion
) -> None:
    exports_api.export_data()

    with open(
        os.path.join(tmp_path / "export", "watchlist-collections.json"),
        "r",
    ) as output_file:
        file_content = json.load(output_file)

    assert file_content == snapshot_json
