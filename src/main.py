# src/main.py

from typing import NoReturn
from xsd_converter import XSDConverter


def main() -> NoReturn:
    XSDConverter.generate_sample_xml(2)
    XSDConverter.generate_sample_json(3)


if __name__ == "__main__":
    main()
