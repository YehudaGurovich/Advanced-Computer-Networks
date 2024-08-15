import socket
import threading
import os


def handle_client(client_socket, client_address):
    print(f"\nNew connection from {client_address}")

    # Receive the request data
    request_data = client_socket.recv(1024).decode('utf-8')
    print(f"Received request:\n{request_data}")

    # Parse the request
    request_lines = request_data.split('\r\n')
    request_line = request_lines[0]
    method, path, _ = request_line.split()

    print(f"Method: {method}")
    print(f"Path: {path}")

    # Prepare the response
    if path == '/':
        response_body = "<html><body><h1>Welcome to the Home Page</h1></body></html>"
        print("Serving home page")
        status = "200 OK"
        content_type = "text/html"
        content_disposition = ""
    elif path == '/secretmission':
        response_body = "<html><body><h1>Secret Mission</h1><p>This is a secret mission page.</p></body></html><a href='/start'>START</a>"
        print("Serving secret mission page")
        status = "200 OK"
        content_type = "text/html"
        content_disposition = ""
    elif path == '/start':
        file_path = "create_exec.py"
    # if os.path.isfile(file_path):
        with open(file_path, 'rb') as file:
            file_content = file.read()
        response_body = file_content
        status = "200 OK"
        content_type = "application/octet-stream"  # Generic binary type
        content_disposition = f"attachment; filename={os.path.basename(file_path)}"
        # else:
        #     response_body = "<html><body><h1>404 Not Found</h1></body></html>"
        #     status = "404 Not Found"
        #     content_type = "text/html"
        #     content_disposition = ""
    else:
        response_body = "<html><body><h1>404 Not Found</h1></body></html>"
        print(f"Page not found: {path}")
        status = "404 Not Found"
        content_type = "text/html"
        content_disposition = ""

    # Build the HTTP response
    response_header = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(response_body)}\r\n"
        "Connection: close\r\n"
    )
    if content_disposition:
        response_header += f"Content-Disposition: {content_disposition}\r\n"
    response_header += "\r\n"

    # Combine header and body
    if isinstance(response_body, bytes):
        response = response_header.encode('utf-8') + response_body
    else:
        response = response_header.encode(
            'utf-8') + response_body.encode('utf-8')

    # Send the response
    client_socket.send(response)

    # Close the connection
    client_socket.close()
    print(f"Connection closed for {client_address}")


def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    while True:
        client_sock, client_address = server_socket.accept()
        client_handler = threading.Thread(
            target=handle_client, args=(client_sock, client_address))
        client_handler.start()


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 8000
    start_server(HOST, PORT)
