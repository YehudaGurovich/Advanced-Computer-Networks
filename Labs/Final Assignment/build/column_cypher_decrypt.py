from typing import List


def decrypt_column_cipher(key: str, encrypted_message: str) -> str:
    """
    Decrypt a message that was encrypted using the columnar cipher.
    """
    # Calculate the number of rows
    key_length = len(key)
    message_length = len(encrypted_message)
    num_rows = (message_length + key_length - 1) // key_length

    # Create sorted column indices (same as in encryption)
    column_indices = sorted(range(key_length), key=lambda k: key[k])

    # Create empty matrix
    matrix = [[''] * key_length for _ in range(num_rows)]

    # Fill the matrix column by column
    char_index = 0
    for col in column_indices:
        for row in range(num_rows):
            matrix[row][col] = encrypted_message[char_index]
            char_index += 1

    # Read the matrix row by row
    decrypted_message = ''.join(''.join(row) for row in matrix)

    # Remove padding
    return decrypted_message.rstrip('*').replace('*', ' ')


if __name__ == "__main__":
    key = "CYPHER"
    encrypted_message = "TSMNR*GW**TNESB!SNRETS*EIAO*PE!RIIACDAE*H*PTYMEA"
    message = decrypt_column_cipher(key, encrypted_message)
    print(f"Decrypted message: {message}")
