# chat_server.py
import select
import socket

import protocol


def handle_client_request(current_socket, clients_names, data):
    parts = data.split(" ", 2)
    command = parts[0]

    if command == "NAME":
        name = parts[1]
        if name in clients_names:
            return "Name is taken", current_socket
        elif current_socket in clients_names.values():
            return "You have already set your name", current_socket
        else:
            clients_names[name] = current_socket
            return f"HELLO {name}", current_socket
    elif command == "GET_NAMES":
        names = " ".join(clients_names.keys())
        return names, current_socket
    elif command == "MSG":
        if len(parts) < 3:
            return "Invalid MSG format", current_socket
        target_name = parts[1]
        message = parts[2]
        if target_name in clients_names:
            sender_name = [
                name for name, sock in clients_names.items() if sock == current_socket
            ][0]
            full_message = f"{sender_name} SENT {message}"
            return full_message, clients_names[target_name]
        else:
            return "Target name does not exist", current_socket
    elif command == "EXIT":
        for name, sock in clients_names.items():
            if sock == current_socket:
                clients_names.pop(name)
                break
        return "EXIT", current_socket
    else:
        return "Unknown command", current_socket


def print_client_sockets(client_sockets):
    for c in client_sockets:
        print("\t", c.getpeername())


def main():
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((protocol.HOSTING, protocol.SERVER_PORT))
    server_socket.listen()
    print("Listening for clients...")
    client_sockets = []
    messages_to_send = []
    clients_names = {}

    while True:
        read_list = client_sockets + [server_socket]
        ready_to_read, ready_to_write, in_error = select.select(
            read_list, client_sockets, []
        )

        for current_socket in ready_to_read:
            if current_socket is server_socket:
                client_socket, client_address = server_socket.accept()
                print("Client joined!\n", client_address)
                client_sockets.append(client_socket)
                print_client_sockets(client_sockets)
            else:
                print(f"Data from client {current_socket.getpeername()}")
                data = protocol.get_message(current_socket)
                if data == "":
                    print("Connection closed\n")
                    for name, sock in clients_names.items():
                        if sock == current_socket:
                            clients_names.pop(name)
                            break
                    client_sockets.remove(current_socket)
                    current_socket.close()
                else:
                    print(data)
                    response, dest_socket = handle_client_request(
                        current_socket, clients_names, data
                    )
                    if response and dest_socket:
                        messages_to_send.append((dest_socket, response))

        for message in messages_to_send:
            current_socket, data = message
            if current_socket in ready_to_write:
                protocol.create_msg(current_socket, data)
                messages_to_send.remove(message)


if __name__ == "__main__":
    main()
