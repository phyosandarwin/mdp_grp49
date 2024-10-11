import socket

def start_server():
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to an IP address and port
    server_socket.bind(('10.96.49.1', 12345))
    # server_socket.bind(('0.0.0.0', 12345))
    
    # Start listening for incoming connections (max 5 queued connections)
    server_socket.listen(5)
    print("Server listening on port 12345...")
    
    # Accept a connection
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")
    
    # Receive data (max 1024 bytes)
    data = client_socket.recv(1024).decode('utf-8')
    print(f"Received: {data}")
    
    # Send a response
    client_socket.send("Hello from server!".encode('utf-8'))
    
    # Close the connection
    client_socket.close()

if __name__ == '__main__':
    start_server()
