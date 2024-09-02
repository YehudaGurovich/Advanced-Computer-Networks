import json


def open_json_file(filename: str) -> dict:
    """
    Opens a JSON file and returns its content.
    """
    with open(filename, "r") as file:
        return json.load(file)


PARAMETERS = open_json_file("parameters.json")
MESSAGES = open_json_file("messages.json")
