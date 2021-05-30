import os


def ensure_file_path(file_path: str) -> str:
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    return file_path
