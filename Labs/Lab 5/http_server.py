import socket

IP = 'localhost'
PORT = 80
FIXED_RECEIVE_SIZE = 1024
SOCKET_TIMEOUT = 2
FIXED_RESPONSE = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body><h1>THIS IS THE TEST RESPONSE</h1></body></html>"
REDIRECT_PATH = '/redirect'  # Path that will do the 302 redirect


def get_file_data(filename):
    """ Get data from file """
    try:
        with open(filename, 'rb') as file:
            return file.read()
    except IOError:
        return None


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    try:
        if resource == '/':
            resource = '/index.html'
        elif resource == REDIRECT_PATH:
            # Example of 302 redirection
            http_header = "HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n"
            client_socket.send(http_header.encode())
            return

        filename = 'webroot' + resource
        data = get_file_data(filename)
        if data:
            if resource.endswith('.html'):
                http_header = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
            elif resource.endswith('.jpg'):
                http_header = "HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\n\r\n"
            elif resource.endswith('.css'):
                http_header = "HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n"
            elif resource.endswith('.js'):  # ! NOT NECESSARY?
                http_header = "HTTP/1.1 200 OK\r\nContent-Type: text/javascript\r\n\r\n"
            elif resource.endswith('.png'):  # ! EXTRA STUFF?
                http_header = "HTTP/1.1 200 OK\r\nContent-Type: image/png\r\n\r\n"
            else:
                http_header = "HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\n\r\n"
            http_response = http_header.encode() + data
        else:
            http_header = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
            http_response = http_header.encode(
            ) + b"<html><body><h1>404 Not Found</h1></body></html>"
        client_socket.send(http_response)
    except Exception as e:
        # Handle 500 Internal Server Error
        http_header = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\n\r\n"
        http_response = http_header.encode(
        ) + b"<html><body><h1>500 Internal Server Error</h1></body></html>"
        client_socket.send(http_response)
        print(f"Error handling request: {e}")


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL
    """
    try:
        lines = request.split('\r\n')
        method, url, version = lines[0].split()
        if method == 'GET' and version.startswith('HTTP/'):
            return True, url
        else:
            return False, None
    except ValueError:
        return False, None


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')
    # client_socket.send(FIXED_RESPONSE.encode())
    while True:
        try:
            client_request = client_socket.recv(FIXED_RECEIVE_SIZE).decode()
            if not client_request:
                break
            is_valid_http, url = validate_http_request(client_request)
            if is_valid_http:
                print('Got a valid HTTP request')
                handle_client_request(url, client_socket)
                break
            else:
                print('Error: Not a valid HTTP request')
                break
        except socket.timeout:
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    print('Closing connection')
    client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))
    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)


if __name__ == "__main__":
    main()
