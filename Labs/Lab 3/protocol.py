import socket

SERVER_PORT = 7777
HOSTING = "localhost"
DATA_HEADER_SIZE = 8


def create_msg(my_socket: socket.socket, data: str) -> None:
    try:
        # Create the header
        data_length = len(data)
        header = data_length.to_bytes(DATA_HEADER_SIZE, byteorder="big")

        # Calculate the maximum value representable by DATA_HEADER_SIZE bytes
        max_data_length = (256**DATA_HEADER_SIZE) - 1
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


def get_message(my_socket: socket.socket) -> str:
    header_size = DATA_HEADER_SIZE
    header = my_socket.recv(header_size)
    # Convert the header from bytes to an integer
    data_length = int.from_bytes(header, byteorder="big")

    if header_size < len(header):
        raise RuntimeError("Socket connection broken or incomplete header received")

    # Receive the data based on the length
    data = bytearray()
    while len(data) < data_length:
        packet = my_socket.recv(data_length - len(data))
        if not packet:
            raise RuntimeError("Socket connection broken")
        data.extend(packet)
    data = data.decode()

    return data
