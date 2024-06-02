# protocol.py
import struct

HOSTING = "127.0.0.1"
SERVER_PORT = 12345


def create_msg(data):
    length = struct.pack("!I", len(data))
    return length + data.encode()


def get_message(sock):
    length = struct.unpack("!I", sock.recv(4))[0]
    return sock.recv(length).decode()
