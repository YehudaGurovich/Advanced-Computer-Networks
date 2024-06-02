import socket

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    my_socket.connect(("localhost", 20000))
    data = input("Enter a word: ")
    while True:
        if data == "EXIT":
            my_socket.send(data.encode())
            break
        my_socket.send(data.encode())
        data = input("Enter a word: ")

    word_received = my_socket.recv(32).decode()
    print(f"Word received is: {word_received}")
except ConnectionAbortedError:
    print("Connection was aborted")
except ConnectionRefusedError:
    print("Connection was refused, is the server running?")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    my_socket.close()
