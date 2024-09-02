import socket
import time
import threading
import random
import string
from scapy.all import *
from base64 import b64encode
from typing import List
from encryption import generate_column_cipher_encryption
from utils import open_json_file

# Event to synchronize server and client
ready_to_receive = threading.Event()

# Load messages and parameters
MESSAGES = open_json_file("messages.json")
PARAMETERS = open_json_file("parameters.json")

SPLIT_LENGTH = PARAMETERS["split_length"]
TOTAL_NUMBER_OF_PACKETS = PARAMETERS["total_number_of_packets"]
SERVER_IP = PARAMETERS["server_ip"]
SERVER_PORT = PARAMETERS["server_port"]
CLIENT_PORT = PARAMETERS["client_port"]
BUFFER_SIZE = PARAMETERS["buffer_size"]
TIMEOUT = PARAMETERS["timeout"]
MAX_WAIT_TIME = PARAMETERS["max_wait_time"]


def create_message_parts() -> List[str]:
    """
    Creates the message parts to be sent in the packets
    """
    column_cipher_message = generate_column_cipher_encryption(
        PARAMETERS["key"], MESSAGES["column_cipher_message"]).encode()

    padding_length = (SPLIT_LENGTH - (len(column_cipher_message) %
                      SPLIT_LENGTH)) % SPLIT_LENGTH
    padded_message = column_cipher_message + b'\x00' * padding_length

    max_index_length = len(str(len(padded_message) // SPLIT_LENGTH))

    return [
        b64encode(padded_message[i:i + SPLIT_LENGTH]).decode() +
        f"ctf{i // SPLIT_LENGTH:0{max_index_length}d}"
        for i in range(0, len(padded_message), SPLIT_LENGTH)
    ]


def create_fake_message(length: int, max_index: int, max_index_length: int) -> str:
    '''
    Creates fake messages with ftc ending
    '''
    base_fake_message = ''.join(random.choices(
        string.ascii_letters + string.digits, k=length))
    return f"{base_fake_message[:length - 5]}ftc{random.randint(0, max_index):0{max_index_length}d}"


def create_packets() -> List[Packet]:
    '''
    Creates real and fake packets, shuffles them and adds the clue message at the beginning
    '''
    message_parts = create_message_parts()
    message_length = len(message_parts[0])
    max_index = len(message_parts)
    max_index_length = len(str(max_index))

    packets = []

    # Create packets with real message parts
    for part in message_parts:
        packet = Ether(src=RandMAC(), dst=RandMAC()) / \
            IP(src=RandIP(), dst=RandIP()) / \
            UDP(sport=RandShort(), dport=RandShort()) / \
            Raw(part.encode())
        packets.append(packet)

    # Create packets with fake messages
    for _ in range(len(message_parts), TOTAL_NUMBER_OF_PACKETS - 1):
        fake_message = create_fake_message(
            message_length, max_index, max_index_length)
        packet = Ether(src=RandMAC(), dst=RandMAC()) / \
            IP(src=RandIP(), dst=RandIP()) / \
            UDP(sport=RandShort(), dport=RandShort()) / \
            Raw(fake_message.encode())
        packets.append(packet)

    random.shuffle(packets)

    # Insert the MITM message at the beginning
    mitm_packet = Ether(src=RandMAC(), dst=RandMAC()) / \
        IP(src=RandIP(), dst=RandIP()) / \
        UDP(sport=RandShort(), dport=RandShort()) / \
        Raw(MESSAGES["MITM_message"].encode())
    packets.insert(0, mitm_packet)

    return packets


def start_server():
    """
    Starts the server and sends the packets
    """
    packets = create_packets()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind((SERVER_IP, SERVER_PORT))
        print("Server is waiting for the client to be ready...")
        ready_to_receive.wait()
        print("Server is sending packets...")
        client_address = (SERVER_IP, CLIENT_PORT)
        for packet in packets:
            udp_socket.sendto(bytes(packet), client_address)
            time.sleep(0.5)
        print(f"{len(packets)} packets sent.")


def start_client():
    """
    Starts the client and receives the packets
    """
    time.sleep(1)
    ready_to_receive.set()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind((SERVER_IP, CLIENT_PORT))
        print("Client is receiving packets...")
        received_packets = []
        start_time = time.time()
        while time.time() - start_time < MAX_WAIT_TIME and len(received_packets) < TOTAL_NUMBER_OF_PACKETS:
            try:
                udp_socket.settimeout(TIMEOUT)
                packet_data, _ = udp_socket.recvfrom(BUFFER_SIZE)
                packet = Ether(packet_data)
                received_packets.append(packet)
            except socket.timeout:
                print("Timeout occurred, continuing...")

    print(f"Received {len(received_packets)} packets.")
    print("All packets received." if len(received_packets) ==
          TOTAL_NUMBER_OF_PACKETS else "SOMETHING WENT WRONG!")


def main():
    server_thread = threading.Thread(target=start_server)
    client_thread = threading.Thread(target=start_client)
    server_thread.start()
    client_thread.start()
    client_thread.join()
    server_thread.join()
    print("Finished.")


if __name__ == "__main__":
    main()
