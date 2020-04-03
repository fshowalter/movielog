import os
from typing import Any, Dict

from movielog import yaml_file


class ConcreteBase(yaml_file.Base):  # noqa: WPS604
    @classmethod
    def from_yaml_object(cls, yaml_object: Dict[str, Any]) -> "ConcreteBase":
        return ConcreteBase(file_path=None)

    def generate_slug(self) -> str:
        """Test stub."""

    @classmethod
    def folder_path(cls) -> str:
        """Test stub."""

    def as_yaml(self) -> Dict[str, Any]:
        """Test stub."""


def test_it_hydrates_from_yaml_file(tmp_path: str,) -> None:
    yaml = """
      imdb_id: tt0053221
      title: Rio Bravo (1959)
    """

    file_path = os.path.join(tmp_path, "temp.yml")

    with open(file_path, "w") as output_file:
        output_file.write(yaml)

    concrete_base = ConcreteBase.from_file_path(file_path)

    assert concrete_base.file_path == file_path
