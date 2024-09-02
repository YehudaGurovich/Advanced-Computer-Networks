import json


def open_json_file(filename):
    with open(filename, "r") as file:
        return json.load(file)


def write_to_text_file(filename: str, content: str) -> None:
    """
    Writes content to a text file.
    """
    with open(filename, "w") as file:
        file.write(content)

    print(f"Message has been written to {filename}")


# PARAMETERS = open_json_file("parameters.json")
MESSAGES = open_json_file("messages.json")
