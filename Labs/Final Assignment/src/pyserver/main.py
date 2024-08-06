from flask import Flask, request  # type: ignore
from os import environ

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello, World! Coming soon!"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=environ.get(
        "PORT", 8080))  # type: ignore
