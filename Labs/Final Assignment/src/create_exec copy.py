import socket
import time
import threading
import random
import string
import sys
import struct
from base64 import b64encode
from scapy.all import RandMAC, RandIP, RandShort
from encryption import generate_column_cipher_encryption
from utils import open_json_file

# Constants
SPLIT_LENGTH = 12
NUMBER_OF_PACKETS = 30
SERVER_IP = '127.0.0.1'
SERVER_PORT = 9999
CLIENT_PORT = 8888
BUFFER_SIZE = 1024


MESSAGES = open_json_file("messages.json")
PARAMETERS = open_json_file("parameters.json")


def create_packets():
    packets = []

    print(generate_column_cipher_encryption(PARAMETERS["key"],
                                            MESSAGES["column_cipher_message"]))
    # Encode to make the padding easier
    column_cypher_message = generate_column_cipher_encryption(
        PARAMETERS["key"], MESSAGES["column_cipher_message"]).encode()

    # Calculate padding length
    padding_length = (SPLIT_LENGTH - (len(column_cypher_message) %
                      SPLIT_LENGTH)) % SPLIT_LENGTH
    padded_message = column_cypher_message + b'\x00' * padding_length

    # Determine the length needed for number padding
    max_index_length = len(str(len(padded_message) // SPLIT_LENGTH))

    # Create message parts with zero-padded indices
    message_parts = [
        b64encode(padded_message[i:i + SPLIT_LENGTH]).decode() +
        "ctf" + f"{i // SPLIT_LENGTH:0{max_index_length}d}"
        for i in range(0, len(padded_message), SPLIT_LENGTH)
    ]

    # Length of each message part (including "ctf" and zero-padded index)
    message_length = len(message_parts[0])

    # Insert the real hidden message parts into random packets
    for part in message_parts:
        packets.append(part)

    # Add some additional random packets with fake messages of the same length
    for i in range(len(message_parts), NUMBER_OF_PACKETS - 1):
        base_fake_message = ''.join(random.choices(
            string.ascii_letters + string.digits, k=message_length))
        fake_message = base_fake_message + "ftc" + \
            f"{random.randint(0, len(message_parts)):0{max_index_length}d}"
        fake_message = fake_message[:message_length]
        packets.append(fake_message)

    # Unsort the packets
    random.shuffle(packets)

    # Insert the first packet with the direct message
    packets.insert(0, MESSAGES["MITM_message"])

    return packets


def start_server():
    packets = create_packets()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind((SERVER_IP, SERVER_PORT))  # Bind the server socket
        print("Server is sending packets...")
        client_address = (SERVER_IP, CLIENT_PORT)
        udp_socket.sendto(len(packets).to_bytes(
            BUFFER_SIZE, 'big'), client_address)
        for packet in packets:
            udp_socket.sendto(packet.encode(), client_address)
            time.sleep(0.1)  # Short delay to mimic packet sending timing
        print("Packets sent.")


def start_client():
    time.sleep(1)  # Ensure the server has time to start
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind((SERVER_IP, CLIENT_PORT))
        print("Client is receiving packets...")
        packets_length_bytes, _ = udp_socket.recvfrom(BUFFER_SIZE)
        packets_length = int.from_bytes(packets_length_bytes, 'big')
        received_packets = []
        start_time = time.time()
        while len(received_packets) < packets_length and time.time() - start_time < 5:
            try:
                udp_socket.settimeout(1)
                packet, _ = udp_socket.recvfrom(1024)
                received_packets.append(packet.decode())
                print(f"Received: {packet.decode()}")
            except socket.timeout:
                print("Timeout occurred, continuing...")
        print(
            f"Received {len(received_packets)} out of {packets_length} packets.")


def main():
    server_thread = threading.Thread(target=start_server)
    client_thread = threading.Thread(target=start_client)
    server_thread.start()
    client_thread.start()
    client_thread.join()
    server_thread.join()
    print("Finished.")
    sys.exit(0)


if __name__ == "__main__":
    main()
