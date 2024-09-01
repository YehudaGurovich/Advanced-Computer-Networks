from flask import Flask, request, send_file  # type: ignore
from os import environ

app = Flask(__name__)


@app.route("/")
def index():
    return '''
        <h1>Are you sure you want to download this file?</h1>
        <a href="/download_file">Download File</a>
    '''


@app.route("/download_file")
def download_file():
    file_path = "../ctf2.pcap"
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=environ.get(
        "PORT", 8080))  # type: ignore
