# simple_socket_client.py

import socket

class SimpleSocketClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_data(self, data):
        try:
            # Create a socket connection to the specified host and port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.host, self.port))
                print(f"Connected to server at {self.host}:{self.port}")

                # Send data to the server
                client_socket.sendall(data.encode())
                print(f"Sent data: {data}")

                # Receive a response from the server
                response = client_socket.recv(1024).decode()
                print(f"Received response: {response}")
                return response

        except socket.error as e:
            print(f"Socket error: {e}")
            return None
socket_server_ip = "10.96.49.30"
socket_server_port = 8001

# Instantiate the SimpleSocketClient
socket_client = SimpleSocketClient(socket_server_ip, socket_server_port)
