from pathlib import Path


def ensure_file_path(file_path: Path) -> Path:
    if not file_path.parent.exists():
        file_path.mkdir(parents=True)

    return file_path
