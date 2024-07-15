"""Encrypted socket server implementation
   Author: Yehuda Gurovich
   Date: 15/07/2024
"""

import socket
import protocol


def create_server_rsp(cmd: str) -> str:
    """Based on the command, create a proper response"""
    return f"{cmd} command received"


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", protocol.PORT))
    server_socket.listen()
    print("Server is up and running")
    (client_socket, client_address) = server_socket.accept()
    print("Client connected")

    # Diffie Hellman
    # 1 - choose private key
    server_diffie_private_key = protocol.diffie_hellman_choose_private_key()
    # 2 - calc public key
    server_diffie_public_key = protocol.diffie_hellman_calc_public_key(
        server_diffie_private_key)
    # 3 - interact with client and calc shared secret
    protocol.send_data(client_socket, str(server_diffie_public_key))
    client_diffie_public_key = int(protocol.receive_data(client_socket))

    diffie_shared_secret = protocol.diffie_hellman_calc_shared_secret(
        client_diffie_public_key, server_diffie_private_key)

    # RSA
    server_p = protocol.generate_large_prime(protocol.PRIME_BIT_SIZE)
    server_q = protocol.generate_large_prime(protocol.PRIME_BIT_SIZE)
    # Pick public key
    # Calculate matching private key
    server_pq = server_p * server_q
    server_public_key, server_private_key = protocol.generate_rsa_keys(
        server_p, server_q)

    # Exchange RSA public keys with client
    data = f"{server_public_key[0]}#{server_public_key[1]}"
    protocol.send_data(client_socket, data)
    client_public_key_str = protocol.receive_data(client_socket).rsplit("#", 1)
    client_public_key = (
        int(client_public_key_str[0]), int(client_public_key_str[1]))

    while True:
        # Receive client's message
        message = protocol.receive_data(client_socket)
        message = message.rsplit("#", 1)

        # Check if client's message is authentic
        # 1 - separate the message and the MAC
        encrypted_message, input_signature = (message[0], message[1])
        # 2 - decrypt the message
        decrypted_message = protocol.symmetric_encryption(
            encrypted_message, diffie_shared_secret)
        # 3 - calc hash of message
        input_hash = protocol.calc_hash(decrypted_message)
        # 4 - use client's public RSA key to decrypt the MAC and get the hash
        verified_hash = protocol.calc_signature(
            int(input_signature), client_public_key[0], client_public_key[1])
        # 5 - check if both calculations end up with the same result
        if input_hash != verified_hash:
            print("Client's message is not authentic")
            break

        if decrypted_message.upper() == "EXIT":
            break

        print(f"Client's message: {decrypted_message}")

        # Create response. The response would be the echo of the client's message
        response = create_server_rsp(decrypted_message.lower())
        # Encrypt
        response_hash = protocol.calc_hash(response)
        response_signature = protocol.calc_signature(
            response_hash, server_private_key[0], server_private_key[1])
        # apply symmetric encryption to the server's message
        encrypted_response = protocol.symmetric_encryption(
            response, diffie_shared_secret)

        # Send to client
        # Combine encrypted user's message to MAC, send to client
        server_message = f"{encrypted_response}#{response_signature}"
        protocol.send_data(client_socket, server_message)

    print("Closing\n")
    client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    main()
