"""Encrypted socket client implementation
   Author:
   Date:
"""
import protocol
import socket


# RSA_PUBLIC_KEY = ?
# RSA_PRIVATE_KEY = ?


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect(("127.0.0.1", protocol.PORT))

    # Diffie Hellman
    # 1 - choose private key
    client_diffie_private_key = protocol.diffie_hellman_choose_private_key()
    # 2 - calc public key
    client_diffie_public_key = protocol.diffie_hellman_calc_public_key(
        client_diffie_private_key)
    # 3 - interact with client and calc shared secret
    protocol.send_data(my_socket, str(client_diffie_public_key))
    server_diffie_public_key = int(protocol.receive_data(my_socket))

    diffie_shared_secret = protocol.diffie_hellman_calc_shared_secret(
        server_diffie_public_key, client_diffie_private_key)

    # RSA
    client_p = protocol.generate_large_prime(protocol.PRIME_BIT_SIZE)
    client_q = protocol.generate_large_prime(protocol.PRIME_BIT_SIZE)
    # Pick public key
    # Calculate matching private key
    client_pq = client_p * client_q
    client_public_key, client_private_key = protocol.generate_rsa_keys(
        client_p, client_q)

    # Exchange RSA public keys with client
    data = f"{client_public_key[0]}#{client_public_key[1]}"
    protocol.send_data(my_socket, data)
    server_public_key_str = protocol.receive_data(my_socket).rsplit("#", 1)
    server_public_key = (
        int(server_public_key_str[0]), int(server_public_key_str[1]))

    while True:
        user_input = input("Enter command\n")
        # Add MAC (signature)
        # 1 - calc hash of user input
        input_hash = protocol.calc_hash(user_input)
        # 2 - calc the signature
        input_signature = protocol.calc_signature(
            input_hash, client_private_key[0], client_private_key[1])

        # Encrypt
        # apply symmetric encryption to the user's input
        encrypted_input = protocol.symmetric_encryption(
            user_input, diffie_shared_secret)

        # Send to server
        # Combine encrypted user's message to MAC, send to server
        message = f"{encrypted_input}#{input_signature}"
        protocol.send_data(my_socket, message)

        # msg = protocol.create_msg(user_input)
        # my_socket.send(msg.encode())

        if user_input == 'EXIT':
            break

        # Receive server's message
        server_response = protocol.receive_data(my_socket)
        if not server_response:
            print("Something went wrong with the length field")

        # Check if server's message is authentic
        # 1 - separate the message and the MAC
        encrypted_response, response_signature = server_response.rsplit("#", 1)
        # 2 - decrypt the message
        decrypted_response = protocol.symmetric_encryption(
            encrypted_response, diffie_shared_secret)
        # 3 - calc hash of message
        response_hash = protocol.calc_hash(decrypted_response)
        # 4 - use server's public RSA key to decrypt the MAC and get the hash
        verified_hash = protocol.calc_signature(
            int(response_signature), server_public_key[0], server_public_key[1])
        # 5 - check if both calculations end up with the same result
        if response_hash != verified_hash:
            print("Server's message is not authentic")
            break
        # Print server's message
        print(f"Server's message: {decrypted_response}")

    print("Closing\n")
    my_socket.close()


if __name__ == "__main__":
    main()
