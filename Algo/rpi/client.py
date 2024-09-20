import socket
import time

def rpi_connect():
    # Configure the client
    server_ip = "192.168.31.31"  # Replace with your PC's IP address
    server_port = 8001  # Use the same port number as on your PC

    # Create a socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect((server_ip, server_port))

    print("Press 0 to read, Press 1 to write")
    while True:
        try:
            option = input("Option: ")
            if int(option) == 0:
                # receive data from server
                data = client_socket.recv(2048)

                print(f"Received: {data.decode('utf-8')}")
            else:
                # Send data to the server
                message = bytes(input("Msg to RPI: "), "utf-8")
                # message = b"Hi RPI"
                client_socket.send(message)

        except ConnectionResetError or KeyboardInterrupt:
            print("Connection closed by server")
            break

    # while True:
    #     try:
    #         data = client_socket.recv(2048)
    #         print(f"Received: {data.decode('utf-8')}")

    #     except ConnectionResetError or KeyboardInterrupt:
    #         print("Connection closed by server")
    #         break

    message = bytes(input("Msg to RPI: "), "utf-8")
    print(message)
