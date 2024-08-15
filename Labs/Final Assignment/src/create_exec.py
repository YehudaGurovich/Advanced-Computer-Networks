import socket
import time
import threading
import pickle
import base64
import random
import string
import sys
from scapy.all import RandMAC, RandIP, RandShort

# Constants
SPLIT_LENGTH = 12
NUMBER_OF_PACKETS = 30
SERVER_IP = '127.0.0.1'
SERVER_PORT = 9999


def create_packets():
    packets = []
    real_hidden_message = "The mystery to be solved lies ahead. Be careful on the way!"
    pickle_message = pickle.dumps(real_hidden_message)

    # Calculate padding length
    padding_length = (SPLIT_LENGTH - (len(pickle_message) %
                      SPLIT_LENGTH)) % SPLIT_LENGTH
    padded_pickle_message = pickle_message + b'\x00' * padding_length

    # Determine the length needed for number padding
    max_index_length = len(str(len(padded_pickle_message) // SPLIT_LENGTH))

    # Create message parts with zero-padded indices
    message_parts = [
        base64.b64encode(padded_pickle_message[i:i + SPLIT_LENGTH]).decode() +
        "ctf" + f"{i // SPLIT_LENGTH:0{max_index_length}d}"
        for i in range(0, len(padded_pickle_message), SPLIT_LENGTH)
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
    packets.insert(0, "Beware of the 64 pickles!")

    return packets


def start_server():
    packets = create_packets()

    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Server is sending packets...")

    for packet in packets:
        # Send the packet to the client
        udp_socket.sendto(packet.encode(), (SERVER_IP, SERVER_PORT))
        time.sleep(0.1)  # Short delay to mimic packet sending timing

    print("Packets sent.")
    # udp_socket.close()

# Client function


def start_client():
    time.sleep(1)  # Ensure the server has time to start

    # Create a UDP socket for receiving
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((SERVER_IP, SERVER_PORT))

    print("Client is receiving packets...")

    received_packets = []
    start_time = time.time()

    while time.time() - start_time < 5:  # Listen for 5 seconds
        packet, addr = udp_socket.recvfrom(65535)
        received_packets.append(packet)
        print("AAAAAAAAAAAAAAAAAAA")

    print(f"Received {len(received_packets)} packets.")
    udp_socket.close()

# Main function to execute server and client


def main():
    server_thread = threading.Thread(target=start_server)
    client_thread = threading.Thread(target=start_client)

    server_thread.start()
    client_thread.start()

    client_thread.join()
    server_thread.join()
    sys.exit(0)


if __name__ == "__main__":
    main()
