import select
import socket

import protocol


def handle_client_request(
    current_socket: socket.socket, clients_names: dict, data: str
) -> tuple:
    # Split the data into 3 parts depending on the command
    data_list = data.split(" ", 2)
    command = data_list[0]
    # NAME <name> will set name. Server will reply error if duplicate
    if command == protocol.NAME_COMMAND:
        if len(data_list) < 2:
            return "Invalid NAME format", current_socket
        name = data_list[1]
        if current_socket in clients_names.values():
            return "You have already set your name", current_socket
        elif name == "":
            return "Name cannot be empty", current_socket
        elif name in clients_names:
            return f"{name} is already taken", current_socket
        else:
            clients_names[name] = current_socket
            return f"HELLO {name}", current_socket
    # GET_NAMES will get all names
    elif command == protocol.GET_NAMES_COMMAND:
        names = " ".join(clients_names.keys())
        return names, current_socket
    # MSG <NAME> <message> will send message to client name
    elif command == protocol.MSG_COMMAND:
        if len(data_list) < 3:
            return "Invalid MSG format", current_socket
        target_name = data_list[1]
        message = data_list[2]
        if message.strip() == "" or target_name.strip() == "":
            return "Invalid MSG format", current_socket
        if target_name not in clients_names:
            return "Target name does not exist", current_socket
        if current_socket not in clients_names.values():
            return "You must set your name first", current_socket
        else:
            sender_name = [
                name for name, sock in clients_names.items() if sock == current_socket
            ][0]
            full_message = f"{sender_name} SENT {message}"
            return full_message, clients_names[target_name]
    # EXIT will close client, remove name from clients_names
    elif command == protocol.EXIT_COMMAND:
        for name, sock in clients_names.items():
            if sock == current_socket:
                clients_names.pop(name)
                current_socket.close()
                break
        return protocol.EXIT_COMMAND, current_socket
    else:
        return "Unknown command", current_socket


def print_client_sockets(client_sockets: list) -> None:
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
        ready_to_read, ready_to_write, _ = select.select(
            read_list, client_sockets, [])

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
