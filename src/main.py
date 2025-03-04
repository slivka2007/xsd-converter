# src/main.py

from typing import NoReturn
from api.xsd_converter_api import create_app


def main() -> NoReturn:
    """Run the application using the application factory pattern."""
    app = create_app(index_html="index.html")
    app.run(debug=True)


if __name__ == "__main__":
    main()
