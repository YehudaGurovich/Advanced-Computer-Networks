# ####################################### #
# Title: SMTP_client.py
# Author: Yehuda Gurovich
# Course: Avanced Computer Networks
# Lab Number: 2
# ###################################### #

import base64
import datetime
import re
import socket

import SMTP_protocol

CLIENT_NAME = "client.net"


def send_data(my_socket: socket.socket, data: str) -> None:
    # Create the header
    try:
        data_length = len(data)
        header = data_length.to_bytes(
            SMTP_protocol.DATA_HEADER_SIZE, byteorder="big")

        # Calculate the maximum value representable by DATA_HEADER_SIZE bytes
        max_data_length = (256**SMTP_protocol.DATA_HEADER_SIZE) - 1
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
    print(data)
    return data


def initialize_conection() -> socket.socket:
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        my_socket.connect((SMTP_protocol.CLIENT_ADDRESS, SMTP_protocol.PORT))
        print("Connected to the server\n".upper())
        return my_socket
    except ConnectionAbortedError:
        print("Failed to establish the conection")


def create_EHLO():
    return f"EHLO {CLIENT_NAME}\r\n".encode()


def check_response_code(response: str, expected_code: str) -> bool:
    if not response.startswith(expected_code):
        print("Error connecting")
        return False
    return True


def is_valid_email(email):
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(regex, email) is not None


def main():
    # Connect to server
    my_socket = initialize_conection()

    # 1 server welcome message
    # Receive response from server
    receive_data(my_socket)

    # 2 EHLO message
    message = create_EHLO()
    my_socket.send(message)

    # Receive response from server and check if it is according to the protocol
    response = my_socket.recv(1024).decode()
    print(response)
    if not response.startswith(SMTP_protocol.REQUESTED_ACTION_COMPLETED):
        print("Error connecting")
        my_socket.close()
        return

    # 3 AUTH LOGIN
    send_data(my_socket, SMTP_protocol.AUTH_TYPE)
    # Receive response from server
    auth_permission = receive_data(my_socket)
    if not check_response_code(auth_permission, SMTP_protocol.AUTH_INPUT):
        print("Error")
        my_socket.close()
        return

    # 4 User #! DO THIS WITH BASE64
    user = "barbie"
    my_socket.send(base64.b64encode(user.encode()))
    # Receive response from server
    user_accepted_code = receive_data(my_socket)
    if not check_response_code(user_accepted_code, SMTP_protocol.AUTH_INPUT):
        print("Error")
        my_socket.close()
        return

    # 5 password #! DO THIS WITH BASE64
    password = "helloken"
    my_socket.send(base64.b64encode(password.encode()))
    # Receive response from server
    auth_accepted_code = receive_data(my_socket)
    if not check_response_code(auth_accepted_code, SMTP_protocol.AUTH_SUCCESS):
        print("Error")
        my_socket.close()
        return

    # 6 mail from
    # Send mail from command and the sender email address
    email = "example@myemail.com"
    if not is_valid_email(email):
        print("Invalid email address")
        my_socket.close()
        return

    email_full_format = "MAIL FROM: <" + email + ">"
    send_data(my_socket, email_full_format)
    # Receive response from server
    mail_from_received = receive_data(my_socket)
    if not check_response_code(
        mail_from_received, SMTP_protocol.REQUESTED_ACTION_COMPLETED
    ):
        print("Error")
        my_socket.close()
        return

    # 7 rcpt to
    # Send rcpt to command and the receiver email address
    receiver_email_list = [
        "email1@tryingemails.com", "email2@tryingemails.com"]
    len_receiver_email_list = len(receiver_email_list)
    counter = 0
    while len_receiver_email_list > counter:
        full_sender_format = "RCPT TO: <" + receiver_email_list[counter] + ">"
        send_data(my_socket, full_sender_format)
        counter += 1
        receiver_email_received = receive_data(my_socket)
        if not check_response_code(
            receiver_email_received, SMTP_protocol.REQUESTED_ACTION_COMPLETED
        ):
            print("Error")
            my_socket.close()
            return

    # 8 data
    # Send data command
    send_data(my_socket, SMTP_protocol.DATA_COMMAND)
    # Receive response from server
    correct_data_message = receive_data(my_socket)
    if not correct_data_message.startswith(SMTP_protocol.ENTER_MESSAGE):
        print("Error")
        my_socket.close()
        return

    # 9 email content
    email_text = (
        f"""
From: {email}
To: {", ".join(receiver_email_list)}
Subject: Test email
Date: {datetime.datetime.now()}
This is a test email
Don't worry about it
Forget you ever saw this :)
"""
        + SMTP_protocol.EMAIL_END
    )
    send_data(my_socket, email_text)

    # Receive response from server
    email_content_received = receive_data(my_socket)
    if not check_response_code(
        email_content_received, SMTP_protocol.REQUESTED_ACTION_COMPLETED
    ):
        print("Error")
        my_socket.close()
        return

    # 10 quit
    send_data(my_socket, SMTP_protocol.CLIENT_QUIT)
    # Receive response from server
    final_response = receive_data(my_socket)
    if not final_response.startswith(SMTP_protocol.SERVER_QUIT):
        print("Error")
        my_socket.close()
        return

    print("CLOSING THE CONNECTION")
    my_socket.close()


if __name__ == "__main__":
    main()
