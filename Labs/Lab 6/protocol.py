"""Encrypted sockets implementation
   Author: Yehuda Gurovich
   Date: 15/07/2024
"""

import random
import socket
from hashlib import sha256
from typing import Tuple

LENGTH_FIELD_SIZE = 64
PORT = 8820

PRIME_BIT_SIZE = 32

DIFFIE_HELLMAN_P = 151
DIFFIE_HELLMAN_G = 223


def symmetric_encryption(input_data: str, key: int) -> str:
    """Return the encrypted / decrypted data
    The key is 16 bits. If the length of the input data is odd, use only the bottom 8 bits of the key.
    Use XOR method"""
    if len(input_data) % 2 == 0:
        key = key & 0x00FF

    new_data = []
    for i in range(len(input_data)):
        new_data.append(chr(ord(input_data[i]) ^ key))

    return "".join(new_data)


def diffie_hellman_choose_private_key() -> int:
    """Choose a 16 bit size private key """
    return random.getrandbits(16)


def diffie_hellman_calc_public_key(private_key: int) -> int:
    """G**private_key mod P"""
    return pow(DIFFIE_HELLMAN_G, private_key, DIFFIE_HELLMAN_P)


def diffie_hellman_calc_shared_secret(other_side_public: int, my_private: int) -> int:
    """other_side_public**my_private mod P"""
    return pow(other_side_public, my_private, DIFFIE_HELLMAN_P)


def calc_hash(message: str) -> int:
    """Create some sort of hash from the message
    Result must have a fixed size of 16 bits"""
    sha256_hash = sha256()
    sha256_hash.update(message.encode())
    return int(sha256_hash.hexdigest(), 16) & 0xFFFF


def calc_signature(hash: int, RSA_private_key: int, pq: int) -> int:
    """Calculate the signature, using RSA algorithm
    hash**RSA_private_key mod (P*Q)"""
    return pow(hash, RSA_private_key, pq)


def generate_rsa_keys(p: int, q: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Calculate the public key for the RSA algorithm"""
    pq = p * q
    phi = (p - 1) * (q - 1)

    e = coprime_int_between(2, phi - 1)
    while True:
        e = random.randint(2, phi - 1)
        if coprime(e, phi):
            break
    d = inverse_mod(e, phi)
    public_key = (e, pq)
    private_key = (d, pq)
    return public_key, private_key


def coprime_int_between(a: int, b: int) -> int:
    while True:
        e = random.randint(a, b)
        if coprime(e, b + 1):
            return e


def send_data(my_socket: socket.socket, data: str) -> None:
    """Send data to the socket, following the protocol using a fixed length header"""

    # Log the data that is being sent
    # print(f"Sent: {data}")

    try:
        # Create the header
        data_length = len(data)
        header = data_length.to_bytes(
            LENGTH_FIELD_SIZE, byteorder="big")

        # Calculate the maximum value representable by DATA_HEADER_SIZE bytes
        max_data_length = (256 ** LENGTH_FIELD_SIZE) - 1
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
    """Receive data from the socket, following the protocol using a fixed length header"""
    header_size = LENGTH_FIELD_SIZE
    header = my_socket.recv(header_size)
    # Convert the header from bytes to an integer
    data_length = int.from_bytes(header, byteorder="big")

    if header_size < len(header):
        print("Something went wrong with the length field")
        raise RuntimeError(
            "Socket connection broken or incomplete header received")

    # Receive the data based on the length
    bytes_data = bytearray()
    while len(bytes_data) < data_length:
        packet = my_socket.recv(data_length - len(bytes_data))
        if not packet:
            raise RuntimeError("Socket connection broken")
        bytes_data.extend(packet)
    data = bytes_data.decode()

    # print(f"Received: {data}")
    return data


def miller_rabin(n: int, k: int = 5) -> bool:
    """Miller-Rabin primality test
    Obtained from the internet, source: https://www.geeksforgeeks.org/primality-test-set-3-miller-rabin/
    Checks if a number is prime or not."""
    if n == 2 or n == 3:
        return True
    if n % 2 == 0 or n == 1:
        return False

    # Write (n - 1) as d * 2^r
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    # Witness loop
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def is_prime(n: int) -> bool:
    """Check if a number is prime. Works for smaller bit size numbers"""
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def coprime(a: int, b: int) -> bool:
    """Check if two numbers are coprime"""
    while b:
        a, b = b, a % b
    return a == 1


def inverse_mod(a: int, m: int) -> int:
    """Calculate the modular multiplicative inverse of a mod m"""
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1


def generate_large_prime(bit_length: int = PRIME_BIT_SIZE) -> int:
    """Generate a large prime number of at least 'bit_length' bits."""
    while True:
        num = random.getrandbits(bit_length)
        # Ensure the number has the correct bit length and is odd
        num |= (1 << bit_length - 1) | 1
        if miller_rabin(num):
            return num


if __name__ == "__main__":
    # Example usage:
    # random.seed(0)
    prime_17_bit = generate_large_prime(17)
    print(f"17-bit prime: {prime_17_bit}")
    print(is_prime(prime_17_bit))

    prime_18_bit = generate_large_prime(18)
    print(f"18-bit prime: {prime_18_bit}")
    print(is_prime(prime_18_bit))

    prime_32_bit = generate_large_prime()
    print(f"32-bit prime: {prime_32_bit}")
    print(is_prime(prime_32_bit))

    print("The numbers are coprime?", coprime(
        random.getrandbits(32), prime_32_bit))
