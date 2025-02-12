# src/main.py
from typing import NoReturn
from pathlib import Path
from xml_generator import XmlGenerator


def main() -> NoReturn:
    project_dir = Path(__file__).parent.parent
    schemas_dir = project_dir / "schemas"
    xsd_path = schemas_dir / "template.xsd"

    output_dir = project_dir / "output"
    xml_path = output_dir / "sample_output.xml"

    xml_generator = XmlGenerator(xsd_path, xml_path)
    xml_generator.generate_sample_xml()


if __name__ == "__main__":
    main()
