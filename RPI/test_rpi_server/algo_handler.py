import socket
import json
import threading
import logging
import time
import queue
import sys
from config import Config
class AlgoHandler:
    def __init__(self, host='10.96.49.1', port=Config.ALGO_PORT_NUMBER):
        self.host = host
        self.port = port
        self.server_socket = None
        self.conn = None
        self.addr = None
        self.running = False  # Flag to control the server's running state
        self.lock = threading.Lock()  # To protect shared resources
        self.message_queue = []  # Queue for messages to send
        self.receive_queue = queue.Queue()  # Queue to store received messages
        self.sender_thread = None
        self.receiver_thread = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def start_server(self):
        """Starts the AlgoHandler server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.server_socket.settimeout(1.0)  # Set timeout to allow periodic checks
        self.running = True
        self.logger.info(f"AlgoHandler server started on {self.host}:{self.port}")
    
        try:
            while self.running:
                try:
                    self.logger.debug("Waiting for a connection...")
                    self.conn, self.addr = self.server_socket.accept()
                    self.logger.info(f"Connection from {self.addr}")
    
                    # Start receiver and sender threads
                    self.receiver_thread = threading.Thread(target=self.receive_messages, daemon=True)
                    self.sender_thread = threading.Thread(target=self.process_send_messages, daemon=True)
                    self.receiver_thread.start()
                    self.sender_thread.start()
    
                    # Wait for the receiver thread to finish (e.g., client disconnects)
                    self.receiver_thread.join()
                    self.logger.info("Receiver thread has terminated.")
    
                    # After receiver thread ends, stop sending messages
                    self.running = False  # Signal sender thread to stop
                    self.sender_thread.join()
                    self.logger.info("Sender thread has terminated.")
    
                except socket.timeout:
                    continue  # Loop back and check if the server should keep running
                except Exception as e:
                    self.logger.error(f"Error accepting connections: {e}")
                    break
    
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received. Stopping the server...")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
        finally:
            self.stop_server()
    
    def process_send_messages(self):
        """Continuously check the message queue and send messages."""
        while self.running:
            if self.message_queue:
                with self.lock:
                    message = self.message_queue.pop(0)  # Get the next message from the queue
                self.send_message(message)
            else:
                time.sleep(0.1)  # Sleep briefly if there's no message to send
    
    def send_message(self, message):
        """Send a message to the connected client."""
        if self.conn:
            try:
                self.conn.sendall(message.encode())
                self.logger.debug(f"Sent: {message}")
            except Exception as e:
                print(f"ERROR SENDING {message}")
                self.logger.error(f"Error sending message: {e}")
                self.running = False  # Stop the server if sending fails
    
    def receive_messages(self, buffer_size=1024):
        while self.running:
            if self.conn:
                try:
                    self.conn.settimeout(1.0)
                    data = self.conn.recv(buffer_size)  # Receive up to specified bytes
                    if data:
                        message = data.decode()
                        self.logger.debug(f"Received: {message}")
                        self.receive_queue.put(message)  # Enqueue the received message
                    else:
                        self.logger.info("Client disconnected.")
                        self.running = False
                        break
                except socket.timeout:
                    continue  # Allow loop to check the running flag
                except Exception as e:
                    self.logger.error(f"Error receiving message: {e}")
                    self.running = False
                    break
    
    def close_connection(self):
        """Close client and server sockets."""
        if self.conn:
            try:
                self.conn.close()
                self.logger.info("Client connection closed.")
            except Exception as e:
                self.logger.error(f"Error closing client connection: {e}")
    
        if self.server_socket:
            try:
                self.server_socket.close()
                self.logger.info("Server socket closed.")
            except Exception as e:
                self.logger.error(f"Error closing server socket: {e}")
    
    def stop_server(self):
        """Stops the AlgoHandler server gracefully."""
        self.running = False
        self.close_connection()
        self.logger.info("AlgoHandler stop signal sent.")
    def send_external_message(self, message):
        """Method to add a message to the queue for sending."""
        # Serialize message if it's not a string
        if isinstance(message, (list, dict)):
            try:
                message = json.dumps(message)
                self.logger.debug(f"Serialized message: {message}")
            except (TypeError, ValueError) as e:
                self.logger.error(f"Error serializing message: {e}")
                return  # Do not enqueue the message if serialization fails
        elif not isinstance(message, str):
            message = str(message)  # Convert other types to string

        with self.lock:
            self.message_queue.append(message)
            self.logger.debug(f"Message queued: {message}")
    def receive_message(self, timeout=5):
        """Retrieve a message from the receive queue with a timeout."""
        try:
            message = self.receive_queue.get(timeout=timeout)
            self.logger.debug(f"Retrieved message from receive_queue: {message}")
            return message
        except queue.Empty:
            self.logger.warning("No message received within the timeout period.")
            return None


    def is_connected(self):
        """Check if a client is connected."""
        return self.conn is not None
    def restart_server_on_new_port(self, new_port):
        """Closes current connection if open and starts the server on a new port."""
        self.logger.info(f"Restarting server on new port {new_port}")
        self.stop_server()
        self.port = new_port
        self.start_server()

# if __name__ == "__main__":
#     # Configure logging
#     logging.basicConfig(
#         level=logging.DEBUG,
#         format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
#         handlers=[
#             logging.StreamHandler(sys.stdout)
#         ]
#     )
    
#     server = AlgoHandler()
#     server_thread = threading.Thread(target=server.start_server, daemon=True)
#     server_thread.start()
    
#     # Wait for the server to establish a connection before prompting for input
#     while not server.is_connected() and server.running:
#         time.sleep(1)  # Polling delay while waiting for a connection
    
#     words = ["Hello", "world", "this", "is", "a", "test", "of", "the", "server"]
    
#     # Add each word to the message queue
#     for word in words:
#         server.send_external_message(word)
    
#     # Example of sending messages from the main thread
#     try:
#         while server.running:
#             msg = input("Enter a message to send to the client (type 'exit' to quit): ")
#             if msg.strip().lower() == 'exit':
#                 server.stop_server()
#                 break
#             server.send_external_message(msg)  # Add message to the queue for sending
#     except KeyboardInterrupt:
#         server.stop_server()
#         print("Main thread interrupted. Exiting...")
    
#     # Ensure server thread is closed properly
#     server_thread.join(timeout=2)  # Give a timeout to avoid waiting indefinitely
#     print("Server thread has been joined. Exiting main program.")
