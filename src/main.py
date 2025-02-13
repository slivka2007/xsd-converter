import json
from typing import NoReturn
from pathlib import Path
from xml_generator import XmlGenerator


def load_config(config_path: Path) -> dict:
    with open(config_path, "r") as config_file:
        return json.load(config_file)


def main() -> NoReturn:
    project_dir = Path(__file__).parent.parent
    config_path = project_dir / "config.json"
    config = load_config(config_path)

    schemas_dir = project_dir / "schemas"
    xsd_path = schemas_dir / config["xsd_file"]

    output_dir = project_dir / "output"
    xml_path = output_dir / config["xml_file"]
    json_path = output_dir / config["json_file"]

    xml_generator = XmlGenerator(xsd_path, xml_path, json_path)
    xml_generator.generate_sample_xml()


if __name__ == "__main__":
    main()
