import socket
import json
import threading
import logging

class AlgoHandler_2:
    def __init__(self, host='10.96.49.1', port=8005):
        self.host = host
        self.port = port
        self.server_socket = None
        self.conn = None
        self.addr = None
        self.running = False
        self.device_connected = False  # Flag to indicate device connection
        self.lock = threading.Lock()  # To protect shared resources
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def start_server(self):
        """Start the AlgoHandler server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.server_socket.settimeout(5.0)  # Set timeout to allow periodic check of self.running
        self.running = True
        self.logger.info(f"AlgoHandler server started on {self.host}:{self.port}")
        
        while self.running and not self.device_connected:
            try:
                self.logger.debug("Waiting for a connection...")
                self.conn, self.addr = self.server_socket.accept()
                self.device_connected = True  # Set the flag when a device connects
                self.logger.info(f"Device connected from {self.addr}")
                
                # Handle client in a separate thread
                client_thread = threading.Thread(target=self.handle_client, args=(self.conn, self.addr), daemon=True)
                client_thread.start()
            except socket.timeout:
                continue  # Timeout occurred, loop back and check if still running
            except Exception as e:
                if self.running:
                    self.logger.error(f"AlgoHandler server error: {e}")
        
        if self.device_connected:
            self.logger.info("A device is connected. No longer accepting new connections.")
        self.server_socket.close()
        self.logger.info("AlgoHandler server stopped listening for new connections.")
    
    def handle_client(self, conn, addr):
        """Handle communication with a connected client."""
        with conn:
            while self.running:
                try:
                    data = conn.recv(1024)
                    if not data:
                        self.logger.info(f"Client {addr} disconnected.")
                        break
                    message = data.decode()
                    client_port_number = addr[-1]
                    self.logger.info(f"Received from {addr}: {message} port: {client_port_number}")
                    # Process the message as needed
                    response = self.process_message(message,client_port_number)
                    conn.sendall(response.encode())
                except Exception as e:
                    self.logger.error(f"Error handling client {addr}: {e}")
                    break
        # Reset the device_connected flag when client disconnects
        with self.lock:
            self.device_connected = False
            self.conn = None
            self.addr = None
            self.logger.info("Device disconnected. Server is ready to accept a new connection.")
    
    def process_message(self, message, client_port_number):
        """Process the received message and prepare a response."""
        try:
            data = json.loads(message)
            self.logger.debug(f"Processing data: {data}")
            message = "MSG_FROM_RPI" 
            response = {"android_message": message ,"client_port_number":client_port_number}
            return json.dumps(response)
        except json.JSONDecodeError:
            self.logger.error("Received invalid JSON.")
            return json.dumps({"status": "error", "message": "Invalid JSON"})
    
    def send_message(self, message):
        """Send a message to the connected client."""
        with self.lock:
            if self.conn:
                try:
                    self.conn.sendall(message.encode())
                    self.logger.info(f"Sent: {message}")
                except Exception as e:
                    self.logger.error(f"Error sending message: {e}")
    
    def receive_message(self, buffer_size=1024):
        """Receive a message from the connected client."""
        with self.lock:
            if self.conn:
                try:
                    data = self.conn.recv(buffer_size)
                    message = data.decode()
                    self.logger.info(f"Received: {message}")
                    return message
                except Exception as e:
                    self.logger.error(f"Error receiving message: {e}")
        return None
    
    def close_connection(self):
        """Close the client and server sockets."""
        with self.lock:
            if self.conn:
                try:
                    self.conn.close()
                    self.logger.info("Client connection closed.")
                except Exception as e:
                    self.logger.error(f"Error closing client connection: {e}")
                self.conn = None
            if self.server_socket:
                try:
                    self.server_socket.close()
                    self.logger.info("Server socket closed.")
                except Exception as e:
                    self.logger.error(f"Error closing server socket: {e}")
                self.server_socket = None
    
    def stop_server(self):
        """Stop the AlgoHandler server gracefully."""
        self.logger.info("Stopping AlgoHandler server...")
        self.running = False
        # Close the server socket to unblock accept()
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                self.logger.error(f"Error closing server socket during stop: {e}")
        # Optionally, close the client connection
        self.close_connection()
    def handle_user_input(self):
        """Handle user input to send messages to the connected client."""
        while self.running:
            message = input("Enter message to send to client: ")
            if message.strip().lower() == 'exit':
                self.stop_server()
                break
            self.send_message(message)

if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    
    # Create the server instance
    server = AlgoHandler_2()
    
    # Start the server in a separate thread so it runs in the background
    server_thread = threading.Thread(target=server.start_server, daemon=True)
    server_thread.start()
    
    # Keep the main thread alive to allow handling user inputs or server interaction
    try:
        server.handle_user_input()
    except KeyboardInterrupt:
        server.stop_server()
    
    # Wait for the server thread to finish
    server_thread.join()
