import socket
import threading
import os
import logging
from google.cloud import logging as cloud_logging
from generate_htmls import generate_home_page, generate_secret_mission_page, add_secret_field

# USE IF RUNNING ON CLOUD

# Initialize Cloud Logging
client = cloud_logging.Client()
client.setup_logging()

# Setup Python logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_client(client_socket, client_address):
    logger.info(f"New connection from {client_address}")

    try:
        # Receive the request data
        request_data = client_socket.recv(1024).decode('utf-8')
        logger.info(f"Received request:\n{request_data}")

        # Parse the request
        request_lines = request_data.split('\r\n')
        request_line = request_lines[0]
        parts = request_line.split()
        if len(parts) != 3:
            logger.error(f"Invalid request line: {request_line}")
            return
        method, path, _ = parts

        # Parse headers
        headers = {}
        for line in request_lines[1:]:
            if ': ' in line:
                header, value = line.split(': ', 1)
                headers[header] = value

        # Check for User-Agent
        user_agent = headers.get('user-agent', '')
        logger.info(f"User-Agent: {user_agent}")
        # Prepare the response
        if path == '/':
            logger.info("Serving home page")
            status = "200 OK"
            content_type = "text/html"
            content_disposition = ""
            response_body = generate_home_page()
            logger.info(f"User-Agent: {user_agent}")
            # Check if the request is from a command-line or script-based environment
            if any(term in user_agent.lower() for term in ["curl", "wget", "powershell", "python-requests"]):
                logger.info("Adding secret field")
                curl_secret = add_secret_field()
                response_body += f"\n{curl_secret}"

        elif path == '/secretmission':
            logger.info("Serving secret mission page")
            status = "200 OK"
            content_type = "text/html"
            content_disposition = ""
            response_body = generate_secret_mission_page()

        elif path == '/secretfile':
            file_path = "packets.exe"
            with open(file_path, 'rb') as file:
                file_content = file.read()
            response_body = file_content
            status = "200 OK"
            content_type = "application/octet-stream"
            content_disposition = f"attachment; filename={os.path.basename(file_path)}"

        elif path == '/finalmessage':
            pass

        else:
            response_body = "<html><body><h1>404 Not Found</h1></body></html>"
            logger.warning(f"Page not found: {path}")
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

    except Exception as e:
        logger.exception(f"Error handling request from {client_address}: {e}")

    finally:
        # Close the connection
        client_socket.close()
        logger.info(f"Connection closed for {client_address}")


def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)

    logger.info(f"Server listening on {host}:{port}")

    while True:
        client_sock, client_address = server_socket.accept()
        client_handler = threading.Thread(
            target=handle_client, args=(client_sock, client_address))
        client_handler.start()


if __name__ == "__main__":
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 8080))
    start_server(HOST, PORT)
