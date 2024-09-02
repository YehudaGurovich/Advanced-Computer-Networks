import json
import sys
import os


def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Accessing directly from the script
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def open_json_file(filename):
    with open(resource_path(filename), "r") as file:
        return json.load(file)


def write_to_text_file(filename: str, content: str) -> None:
    """
    Writes content to a text file.
    """
    with open(filename, "w") as file:
        file.write(content)

    print(f"Message has been written to {filename}")


PARAMETERS = open_json_file("parameters.json")
MESSAGES = open_json_file("messages.json")
