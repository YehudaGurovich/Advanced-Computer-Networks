import msvcrt
import select
import socket
from typing import Literal

import protocol


def move_cursor(cursor_position: int, direction: Literal["right", "left"], msg: str) -> int:
    msg_length = len(msg)

    if direction == "left" and cursor_position > 0:
        print("\b", end="", flush=True)
        return cursor_position - 1

    elif direction == "right" and cursor_position < msg_length:
        print(msg[cursor_position], end="", flush=True)
        return cursor_position + 1

    return cursor_position


def redraw_line(msg: str, cursor_position: int) -> None:
    # Move cursor to the start of the line
    print("\r", end="", flush=True)
    # Clear the line
    print(" " * (len(msg) + 1), end="", flush=True)
    # Print the message
    print("\r" + msg, end="", flush=True)
    # Move cursor to the correct position
    if cursor_position < len(msg):
        print("\r" + msg[:cursor_position], end="", flush=True)


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((protocol.HOSTING, protocol.SERVER_PORT))
    print("Enter commands:")
    print("Empty message will close the connection\n")

    msg = ""
    cursor_position = 0
    while msg != protocol.EXIT_COMMAND:
        rlist, _, _ = select.select([my_socket], [], [], 0.1)
        if rlist:
            response = protocol.get_message(my_socket)
            if response == "" or response == protocol.EXIT_COMMAND:
                print("Server closed connection. Exiting...")
                break
            print(f"S: {response}")

        if msvcrt.kbhit():
            new_char = msvcrt.getch()
            # You can use the arrow keys to move the cursor left and right
            # The delete key will delete the character to the left of the cursor
            # The enter key will send the message
            # The message stays consistent even with arrow keys and delete
            if new_char == b"\xe0":  # Arrow key
                arrow_key = msvcrt.getch()
                if arrow_key == b"K":
                    cursor_position = move_cursor(cursor_position, "left", msg)
                elif arrow_key == b"M":
                    cursor_position = move_cursor(
                        cursor_position, "right", msg)
            elif new_char == b"\r":
                protocol.create_msg(my_socket, msg)
                print()
                msg = ""
                cursor_position = 0
            elif new_char == b"\b":
                if cursor_position > 0:
                    msg = msg[: cursor_position - 1] + msg[cursor_position:]
                    cursor_position = move_cursor(cursor_position, "left", msg)
                    redraw_line(msg, cursor_position)
            else:
                new_char = new_char.decode()
                msg = msg[:cursor_position] + new_char + msg[cursor_position:]
                cursor_position = move_cursor(cursor_position, "right", msg)
                redraw_line(msg, cursor_position)

    my_socket.close()


if __name__ == "__main__":
    main()
