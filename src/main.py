# src/main.py
from typing import NoReturn
from api.xsd_converter_api import create_app

app = create_app(index_html="index.html")

if __name__ == "__main__":
    app.run()
