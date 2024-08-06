# Filename: column_cypher.py

def generate_column_cypher(key: str, message: str) -> str:
    """
    Generate a column cypher from a key and a message
    """
    # Generate the key

    message = message.replace(" ", "*")
    if len(message) % len(key) != 0:
        message += "*" * (len(key) - len(message) % len(key))

    message_list = [message[i:i+len(key)]
                    for i in range(0, len(message), len(key))]

    unsorted_enum_key = list(enumerate(key))

    zipped = list(zip(*message_list))

    sorted_enum_key = list(enumerate(sorted(key)))

    reordered_key = [
        (x[0], y[0]) for x in sorted_enum_key for y in unsorted_enum_key if x[1] == y[1]]

    encrypted_message = [zipped[reordered_key[j][0]] for i in range(
        len(zipped)) for j in range(len(reordered_key)) if reordered_key[j][1] == i]

    return "".join("".join(row) for row in encrypted_message)
    # print("".join("".join(row) for row in zip(*message_list)))


if __name__ == "__main__":
    key = "CYPHER"
    message = "THIS IS AN IMPORTANT ENCRYPTED MESSAGE! BEWARE"
    print(generate_column_cypher(key, message))
