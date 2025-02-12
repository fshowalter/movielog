import gzip
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.fixture
def gzip_file(tmp_path: str) -> Callable[..., Path]:
    def factory(file_path: Path) -> Path:
        output_file_name = f"{Path(file_path).name}.gz"
        output_path = Path(tmp_path) / output_file_name
        with (
            Path.open(file_path, "rb") as input_file,
            gzip.open(output_path, "wb") as output_file,
        ):
            shutil.copyfileobj(input_file, output_file)
        return output_path

    return factory
