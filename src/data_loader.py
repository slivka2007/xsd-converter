# src/data_loader.py

import json
import os
from typing import Any
from pathlib import Path


class DataLoaderError(Exception):
    """Custom exception for DataLoader errors."""
    pass


class DataLoader:
    _root_dir: Path = None
    _config: dict = None
    _initialized: bool = False

    @classmethod
    def _initialize(cls) -> None:
        """Initialize the DataLoader with configuration."""
        if cls._initialized:
            return
        cls._root_dir = Path(__file__).parent.parent
        try:
            cls._config = cls._load_config()
            cls._ensure_directories_exist()
            cls._initialized = True
        except Exception as e:
            raise DataLoaderError(f"Failed to initialize DataLoader: {str(e)}")

    @classmethod
    def _ensure_directories_exist(cls) -> None:
        """Ensure output and schema directories exist."""
        os.makedirs(cls._root_dir / "schemas", exist_ok=True)
        os.makedirs(cls._root_dir / "output", exist_ok=True)

    @classmethod
    def _load_config(cls) -> dict:
        """Load configuration from JSON file."""
        config_path = cls._root_dir / "config.json"
        try:
            with open(config_path, "r") as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            raise DataLoaderError(f"Config file not found: {config_path}")
        except json.JSONDecodeError:
            raise DataLoaderError(f"Invalid JSON in config file: {config_path}")

    @classmethod
    def get_xsd_path(cls) -> Path:
        """Get the path to the XSD file."""
        cls._initialize()
        schemas_dir = cls._root_dir / "schemas"
        return schemas_dir / cls._config["xsd_file"]

    @classmethod
    def get_xml_path(cls) -> Path:
        """Get the path to the XML output file."""
        cls._initialize()
        output_dir = cls._root_dir / "output"
        return output_dir / cls._config["xml_file"]

    @classmethod
    def get_json_path(cls) -> Path:
        """Get the path to the JSON output file."""
        cls._initialize()
        output_dir = cls._root_dir / "output"
        return output_dir / cls._config["json_file"]

    @classmethod
    def load_json_file(cls) -> str:
        """Load the JSON output file."""
        cls._initialize()
        try:
            with open(cls.get_json_path(), "r") as json_file:
                return json_file.read()
        except FileNotFoundError:
            return ""

    @classmethod
    def load_xml_file(cls) -> str:
        """Load the XML output file."""
        cls._initialize()
        try:
            with open(cls.get_xml_path(), "r") as xml_file:
                return xml_file.read()
        except FileNotFoundError:
            return "XML file not found"

    @classmethod
    def load_xsd_file(cls) -> str:
        """Load the XSD schema file."""
        cls._initialize()
        try:
            with open(cls.get_xsd_path(), "r") as xsd_file:
                return xsd_file.read()
        except FileNotFoundError:
            return "XSD file not found"

    @classmethod
    def write_json_file(cls, json_data: str) -> None:
        """Write to the JSON output file."""
        cls._initialize()
        with open(cls.get_json_path(), "w") as json_file:
            json_file.write(json_data)

    @classmethod
    def write_xml_file(cls, xml_data: Any) -> None:
        """Write to the XML output file."""
        cls._initialize()
        with open(cls.get_xml_path(), "wb") as xml_file:
            xml_file.write(xml_data)

    @classmethod
    def write_xsd_file(cls, xsd_data: str) -> None:
        """Write to the XSD schema file."""
        cls._initialize()
        with open(cls.get_xsd_path(), "w") as xsd_file:
            xsd_file.write(xsd_data)
