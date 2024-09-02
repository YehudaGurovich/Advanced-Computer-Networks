import json
import sys
import os


def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, works for dev and for PyInstaller
    Needed for PyInstaller so used in local development as well to avoid issues.
    Does not work in Google Cloud.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Accessing directly from the script
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def open_json_file(filename: str) -> json:
    """
    Opens a JSON file and returns its content.
    """
    with open(resource_path(filename), "r") as file:
        return json.load(file)


PARAMETERS = open_json_file("parameters.json")
MESSAGES = open_json_file("messages.json")
