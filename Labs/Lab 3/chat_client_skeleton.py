import msvcrt
import select
import socket

import protocol

# NAME <name> will set name. Server will reply error if duplicate
# GET_NAMES will get all names
# MSG <NAME> <message> will send message to client name
# EXIT will close client


my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect((protocol.HOSTING, protocol.SERVER_PORT))
print("Enter commands\n")
msg = ""
while msg != "EXIT":
    rlist, wlist, xlist = select.select([my_socket], [], [], 0.1)
    if rlist:
        msg = protocol.get_message(my_socket)

    if msvcrt.kbhit():
        new_char = msvcrt.getch().decode()
        if new_char == '\r':
            protocol.create_msg(my_socket, msg)
            print()
            msg = ""
        elif new_char == '\b':
            if msg:
                msg = msg[:-1]
                print("\b \b", end="", flush=True)
        else:
            msg += new_char
            print(new_char, end="", flush=True)

my_socket.close()
