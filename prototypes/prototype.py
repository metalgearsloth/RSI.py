from typing import List, Union, Iterable
from pathlib import Path
import yaml

from .component import PrototypeComponent


class Prototype:
    def __init__(self,
                 ptype="entity",
                 parent=None,
                 id=None,
                 name=None,
                 description=None,
                 components: List[PrototypeComponent] = None,
                 **kwargs):
        self.ptype = ptype
        self.parent = parent
        self.id = id
        self.name = name
        self.description = description
        self.kwargs = kwargs
        if not components:
            components = []
        self.components = components

    @classmethod
    def _key_sort(cls, string: str) -> int:
        order = [
            "type",
            "abstract",
            "parent",
            "id",
            "name",
            "description",
            "components",
        ]
        return order.index(string) if string in order else 1000

    @classmethod
    def _component_sort(cls, string: str) -> int:
        # In styleguide order as god intended
        order = [
            "Sprite",
            "Icon",
            "Appearance",
            "SnapGrid",
            "Collidable",
            "Physics",
        ]
        return order.index(string) if string in order else 1000

    def to_dict(self) -> dict:
        # Order of insertion important below
        result = {"type": self.ptype}
        if self.parent:
            result.update({"parent": self.parent})
        result.update({
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "components": [x.to_dict() for x in self.components]
        })
        result.update(self.kwargs)

        # dicts are inherently ordered since 3.7
        result = dict(sorted(result.items(), key=lambda x, _: self._key_sort(x)))
        return result

    def append_to_file(self, path: Path) -> None:
        """
        Add this prototype to an existing .yml file.
        WARNING: THIS WILL NUKE COMMENTS AND FORMATTING BECAUSE PYYAML SUCKS.
        :param path:
        :return:
        """
        self.append_multiple_to_file(path, (self, ))

    @classmethod
    def append_multiple_to_file(cls, path: Path, prototypes: Iterable["Prototype"]) -> None:
        """
        Add multiple prototypes to an existing .yml file
        WARNING: THIS WILL NUKE COMMENTS AND FORMATTING BECAUSE PYYAML SUCKS.
        :param path:
        :param prototypes:
        :return:
        """
        if not path.is_file():
            raise FileNotFoundError

        if path.suffix not in ["yml", "yaml"]:
            raise Exception("Not a .yml file")

        with open(path.name, "rb") as f:
            existing = yaml.load(stream=f, Loader=yaml.SafeLoader)

        # If the yaml file's empty / non-existent this can also be empty
        if not existing:
            existing = []

        for prototype in prototypes:
            existing.append(prototype.to_dict())

        with open(path.name, "w") as f:
            yaml.dump(data=existing, stream=f, Dumper=yaml.SafeDumper, default_flow_style=False, sort_keys=False)
        # Format the file to be less bad
        with open(path.name, "r") as f:
            lines = f.readlines()
        with open(path.name, "w") as f:
            f.writelines([f"\n{x}" if x[0:7] == "- type:" else x for x in lines])

    @classmethod
    def from_rsi(cls, path: Path) -> "Prototype":
        """
        Create simple prototypes from .rsi files.
        These will need further enhancements.
        :param path:
        :return:
        """
        if not path.is_dir():
            raise FileNotFoundError

        name = path.stem.replace("_", " ")
        # PascalCase the filepath
        pascal_name = "".join([x.capitalize() for x in path.stem.split("_")])
        rsi_sprite = ""  # TODO: Get relative to repo root
        components = [
            PrototypeComponent(
                ptype="Sprite",
                sprite=rsi_sprite,
            ),
            PrototypeComponent(
                ptyoe="Icon",
                sprite=rsi_sprite,
            )
        ]

        prototype = Prototype(
            ptype="entity",
            id=f"{pascal_name}",
            name=name,
            description="",
            components=components,
        )

        return prototype

    @classmethod
    def from_folder(cls, path: Path) -> List["Prototype"]:
        """
        Convert a folder of .rsis to prototype objects
        :param path:
        :return:
        """
        if not path.is_dir():
            raise NotADirectoryError

        result: List["Prototype"] = []

        for fpath in path.iterdir():
            result.append(cls.from_rsi(fpath))

        return result
