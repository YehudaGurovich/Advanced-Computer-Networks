import socket
import threading
import os
from local_generate_htmls import generate_home_page, generate_secret_mission_page, add_secret_field, generate_final_message_page

# USE IF RUNNING ON LOCALHOST


def handle_client(client_socket, client_address):
    print(f"\nNew connection from {client_address}")

    # Receive the request data
    request_data = client_socket.recv(1024).decode('utf-8')
    print(f"Received request:\n{request_data}")

    # Parse the request
    request_lines = request_data.split('\r\n')
    request_line = request_lines[0]
    parts = request_line.split()
    if len(parts) != 3:
        # Handle the error, e.g., by logging an error message or sending a response
        print("Invalid request line:", request_line)
        return
    method, path, _ = parts

    # Parse headers
    headers = {}
    for line in request_lines[1:]:
        if ': ' in line:
            header, value = line.split(': ', 1)
            headers[header] = value

    # Check for User-Agent
    user_agent = headers.get('User-Agent', '')

    print(f"Method: {method}")
    print(f"Path: {path}")

    # Prepare the response
    if path == '/':
        print("Serving home page")
        status = "200 OK"
        content_type = "text/html"
        content_disposition = ""
        response_body = generate_home_page()
    # Check if the request is from a command-line or script-based environment
        if any(term in user_agent.lower() for term in ["curl", "wget", "powershell", "python-requests"]):
            # Adding custom field in the response
            print("Adding secret field")
            # curl_secret = serialize_with_pickle(generate_SecretRoute())
            curl_secret = add_secret_field()
            response_body += f"\n{curl_secret}"

    elif path == '/secretmission':
        print("Serving secret mission page")
        status = "200 OK"
        content_type = "text/html"
        content_disposition = ""
        response_body = generate_secret_mission_page()

    elif path == '/secretfile':
        file_path = "dist/packets.exe"
        with open(file_path, 'rb') as file:
            file_content = file.read()
        response_body = file_content
        status = "200 OK"
        content_type = "application/octet-stream"  # Generic binary type
        content_disposition = f"attachment; filename={os.path.basename(file_path)}"

    elif path == '/finalmessage':
        print("Serving final message page")
        status = "200 OK"
        content_type = "text/html"
        content_disposition = ""
        response_body = generate_final_message_page()

    else:
        response_body = "<html><body><h1>404 Not Found</h1></body></html>"
        print(f"Page not found: {path}")
        status = "404 Not Found"
        content_type = "text/html"
        content_disposition = ""

        # print(
        #     f"\nPickle: {custom_field}")
        # print(dir(pickle.loads(custom_field)))
        # print(pickle.loads(custom_field)._SecretRoute__route)

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
    PORT = 8080
    start_server(HOST, PORT)
