# ####################################### #
# Title: SMTP_server.py
# Author: Yehuda Gurovich
# Course: Avanced Computer Networks
# Lab Number: 2
# ###################################### #


import base64
import socket

import SMTP_protocol

IP = "localhost"
SOCKET_TIMEOUT = 1
SERVER_NAME = "SMTP_server.com"

user_names = {"shooki": "abcd1234", "barbie": "helloken"}


def send_data(my_socket: socket.socket, data: str) -> None:
    # Log the code and data that is being sent
    print(f"Sent: {data}")

    try:
        # Create the header
        data_length = len(data)
        header = data_length.to_bytes(
            SMTP_protocol.DATA_HEADER_SIZE, byteorder="big")

        # Calculate the maximum value representable by DATA_HEADER_SIZE bytes
        max_data_length = (256 ** SMTP_protocol.DATA_HEADER_SIZE) - 1
        if data_length > max_data_length:
            raise RuntimeError("Data too long")

        data_bytes = data.encode()
        message = header + data_bytes

        # Send the data
        total_sent = 0
        while total_sent < len(message):
            sent = my_socket.send(message[total_sent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            total_sent += sent
    except Exception as e:
        print(e)


def receive_data(my_socket: socket.socket) -> str:
    header_size = SMTP_protocol.DATA_HEADER_SIZE
    header = my_socket.recv(header_size)
    # Convert the header from bytes to an integer
    data_length = int.from_bytes(header, byteorder="big")

    if header_size < len(header):
        raise RuntimeError(
            "Socket connection broken or incomplete header received")

    # Receive the data based on the length
    data = bytearray()
    while len(data) < data_length:
        packet = my_socket.recv(data_length - len(data))
        if not packet:
            raise RuntimeError("Socket connection broken")
        data.extend(packet)
    data = data.decode()

    print(f"Received: {data}")
    return data


# Fill in the missing code
def create_initial_response():
    try:
        return f"{SMTP_protocol.SMTP_SERVICE_READY} {SERVER_NAME} Service ready\r\n"

    except ConnectionRefusedError:
        return "{}".format(SMTP_protocol.SMTP_SERVICE_READY)


# Example of how a server function should look like
def create_EHLO_response(client_message):
    """Check if client message is legal EHLO message
    If yes - returns proper Hello response
    Else - returns proper protocol error code"""
    if not client_message.startswith("EHLO"):
        return ("{}".format(SMTP_protocol.COMMAND_SYNTAX_ERROR)).encode()
    client_name = client_message.split()[1]
    return "{} {} Hello {}\r\n".format(
        SMTP_protocol.REQUESTED_ACTION_COMPLETED, SERVER_NAME, client_name
    ).encode()


def user_auth(user, password):
    if user in user_names and user_names[user] == password:
        return f"{SMTP_protocol.AUTH_SUCCESS} Authentication successful\r\n"
    return f"{SMTP_protocol.INCORRECT_AUTH} Authentication credentials invalid\r\n"


def verify_code(client_socket: socket.socket, response: str, expected_code: str) -> None:
    if not response.startswith(expected_code):
        send_data(client_socket, f"{SMTP_protocol.COMMAND_SYNTAX_ERROR}\r\n")
        client_socket.close()
        exit()


def handle_SMTP_client(client_socket):
    # 1 send initial message
    message = create_initial_response()
    send_data(client_socket, message)

    # 2 receive and send EHLO
    message = client_socket.recv(1024).decode()
    print(message)
    response = create_EHLO_response(message)
    client_socket.send(response)
    if not response.decode().startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print("Error client EHLO")
        return

    # 3 receive AUTH Login
    auth_msg = receive_data(client_socket)
    verify_code(client_socket, auth_msg, SMTP_protocol.AUTH_TYPE)

    # 4 Receive user
    send_data(client_socket, f"{SMTP_protocol.AUTH_INPUT} {
              base64.b64encode("Username:".encode())}\r\n")

    # Receive the username from the client
    user = base64.b64decode(client_socket.recv(1024).decode()).decode()
    print(f"Received: {user}")

    # 5 Receive password
    send_data(client_socket, f"{SMTP_protocol.AUTH_INPUT} {
              base64.b64encode("Password:".encode())}\r\n")

    # Receive the password from the client
    password = base64.b64decode(client_socket.recv(1024).decode()).decode()
    print(f"Received: {password}")

    auth_response = user_auth(user, password)
    send_data(client_socket, auth_response)

    # 6 mail from
    # Receive mail from command and the sender email address
    mail_from = receive_data(client_socket)
    verify_code(client_socket, mail_from, SMTP_protocol.MAIL_FROM_COMMAND)
    # All went well, send 250 OK
    send_data(client_socket, f"{
              SMTP_protocol.REQUESTED_ACTION_COMPLETED} Sender OK \r\n")

    # 7 rcpt to
    # Receive rcpt to command and the receiver email address
    receiver_email_list = []
    while True:
        rcpt_to = receive_data(client_socket)
        if rcpt_to.startswith("DATA"):
            break
        verify_code(client_socket, rcpt_to, SMTP_protocol.RCPT_TO_COMMAND)

        # All went well, add the receiver to the list and send 250 OK
        receiver_email_list.append(rcpt_to)
        send_data(client_socket, f"{
                  SMTP_protocol.REQUESTED_ACTION_COMPLETED} Recipient OK \r\n")

    # 8 DATA
    # Data command was accepted in the previous step to end the loop. Send 354
    send_data(client_socket, f"{
              SMTP_protocol.ENTER_MESSAGE} Start mail input; end with <CRLF>.<CRLF>\r\n")

    # 9 email content
    # Receive email content
    while True:
        email_content = receive_data(client_socket)
        if email_content.endswith(SMTP_protocol.EMAIL_END):
            break
        verify_code(client_socket, email_content, SMTP_protocol.DATA_COMMAND)

    # All went well, send 250 OK
    send_data(client_socket, f"{
              SMTP_protocol.REQUESTED_ACTION_COMPLETED} OK\r\n")

    # 10 quit
    quit_command = receive_data(client_socket)
    verify_code(client_socket, quit_command, SMTP_protocol.CLIENT_QUIT)
    # All went well, send code 221
    send_data(client_socket, f"{SMTP_protocol.SERVER_QUIT}\r\n")


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, SMTP_protocol.PORT))
    server_socket.listen()
    print(f"Listening for connections on ip: {
          IP} and port: {SMTP_protocol.PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print("\nNew connection received\n".upper())
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_SMTP_client(client_socket)
        print("Connection closed".upper())
        exit()


if __name__ == "__main__":
    # Call the main handler function
    main()
