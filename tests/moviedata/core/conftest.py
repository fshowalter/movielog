import gzip
import os
import shutil
from typing import Callable

import pytest


@pytest.fixture
def gzip_file(tmp_path: str) -> Callable[..., str]:
    def factory(file_path: str) -> str:
        output_file_name = "{0}.gz".format(os.path.basename(file_path))
        output_path = os.path.join(tmp_path, output_file_name)
        with open(file_path, "rb") as input_file:
            with gzip.open(output_path, "wb") as output_file:
                shutil.copyfileobj(input_file, output_file)
        return output_path

    return factory
