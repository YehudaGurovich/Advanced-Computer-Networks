import socket

server_socket = socket.socket()

try:
    server_socket.bind(("localhost", 20000))
    server_socket.listen()
    print("SERVER IS CONNECTED")

    (client_socket, client_address) = server_socket.accept()
    print("A CLIENT HAS CONNECTED")

    final_word = []
    while True:
        data = client_socket.recv(32).decode()
        print(f"Word received is: {data}")
        if data == "EXIT":
            print("Client has exited")
            break
        final_word.append(data[0])

    final_word = "".join(final_word)
    client_socket.send(final_word.encode())
except ConnectionError:
    print("Error establishing the connection")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    client_socket.close()
    server_socket.close()
