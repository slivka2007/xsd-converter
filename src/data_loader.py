# src/data_loader.py

import json
from typing import Any
import xmltodict
from pathlib import Path


class DataLoader:
    _root_dir: Path = None
    _config: dict = None
    _initialized: bool = False

    @classmethod
    def _initialize(cls) -> None:
        if cls._initialized:
            return
        cls._root_dir = Path(__file__).parent.parent
        cls._config = cls._load_config()
        _initialized = True

    @classmethod
    def _load_config(cls) -> dict:
        config_path = cls._root_dir / "config.json"
        with open(config_path, "r") as config_file:
            return json.load(config_file)

    @classmethod
    def get_xsd_path(cls) -> Path:
        cls._initialize()
        schemas_dir = cls._root_dir / "schemas"
        return schemas_dir / cls._config["xsd_file"]

    @classmethod
    def get_xml_path(cls) -> Path:
        cls._initialize()
        output_dir = cls._root_dir / "output"
        return output_dir / cls._config["xml_file"]

    @classmethod
    def get_json_path(cls) -> Path:
        cls._initialize()
        output_dir = cls._root_dir / "output"
        return output_dir / cls._config["json_file"]

    @classmethod
    def load_json_file(cls) -> dict:
        cls._initialize()
        with open(cls.get_json_path(), "r") as json_file:
            return json.load(json_file)

    @classmethod
    def load_xml_file(cls) -> dict:
        cls._initialize()
        with open(cls.get_xml_path(), "r") as xml_file:
            return xmltodict.parse(xml_file.read())

    @classmethod
    def write_json_file(cls, json_data: str) -> None:
        cls._initialize()
        with open(cls.get_json_path(), "w") as json_file:
            json_file.write(json_data)

    @classmethod
    def write_xml_file(cls, xml_data: Any) -> None:
        cls._initialize()
        with open(cls.get_xml_path(), "wb") as xml_file:
            xml_file.write(xml_data)
