from utils import open_parameters, write_to_text_file


def generate_column_cipher_encryption(key: str, message: str) -> str:
    """
    Generate a columnar cipher_encryption from a key and a message.
    """
    # Pad the message
    key_length = len(key)
    padded_message = message.replace(" ", "*")
    padding_length = (key_length - len(padded_message) %
                      key_length) % key_length
    padded_message += "*" * padding_length

    # Create the matrix
    matrix = [padded_message[i:i+key_length]
              for i in range(0, len(padded_message), key_length)]

    # Create sorted column indices
    column_indices = sorted(range(key_length), key=lambda k: key[k])

    # Reorder columns and join
    encrypted_message = ''.join(
        ''.join(row[i] for row in matrix) for i in column_indices)

    return encrypted_message


if __name__ == "__main__":
    PARAMETERS_FILE = "parameters.json"
    params = open_parameters(PARAMETERS_FILE)
    key = params["key"]
    message = params["message"]
    encrypted = generate_column_cipher_encryption(key, message)
    print(f"Encrypted message: {encrypted}")
    write_to_text_file("encrypted.txt", encrypted)
