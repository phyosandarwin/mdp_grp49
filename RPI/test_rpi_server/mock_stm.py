import queue
import time
import threading

class STM_Controller(threading.Thread):
    def __init__(self, port, baud_rate, pause_queue, pause_done_event, stm_to_rpi_queue,timeout=1):
        super().__init__()
        self.serial_port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.command_queue = queue.Queue()
        self.ser = None
        self.stm_buffer_time =5#pause between each instrution sent
        self.mock = False  # Start with real mode, switch to mock if connection fails
        self.pause_queue = pause_queue  # Queue to send pause signals
        self.pause_done_event = pause_done_event  # Event to wait for pause completion
        self.running = True  # Control the thread's running state
        self.pause_time = 10#sit still to take pic
        self.stm_to_rpi_queue = stm_to_rpi_queue

    def connect(self):
        """Establish a serial connection to the robot or switch to mock mode if connection fails."""
        try:
            import serial  # Import serial inside the method to handle import error in mock mode
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=self.timeout)
            print(f"Connected to {self.serial_port} at {self.baud_rate} baud rate.")
        except Exception as e:
            print(f"Error connecting to {self.serial_port}: {e}")
            print("[Mock Mode] Switching to mock mode.")
            self.mock = True

    def disconnect(self):
        """Close the serial connection or simulate disconnection in mock mode."""
        if self.mock:
            print(f"[Mock Mode] Simulated disconnection from {self.serial_port}.")
        else:
            if self.ser and self.ser.is_open:
                self.ser.close()
                print(f"Disconnected from {self.serial_port}.")

    def add_command(self, command):
        """Add a single command to the queue."""
        self.command_queue.put(command)
        print(f"Command added: {command}")

    def add_commands(self, commands , send_coords):
        """Add multiple commands to the queue."""
        if isinstance(commands, list):  # Ensure commands is a list
            for i,command in enumerate(commands):
                self.add_command(command)
                self.stm_to_rpi_queue.put(send_coords[i])
                
        else:
            print("Error: add_commands expects a list of commands.")

    def send_next_command(self):
        """Send the next command in the queue to the robot or simulate in mock mode."""
        try:
            # Attempt to get a command with a timeout to allow thread to exit gracefully
            message = self.command_queue.get(timeout=2)
            print(f'message from command queue is {message}')
        except queue.Empty:
            # No command to process at the moment
            print(f'EMPTY QUEUE')
            self.running=False
            return

        if message.startswith('P_'):  # Pause command
            try:
                # Extract the pause time; assuming format 'P___<number>'
                obj_id_str = ''.join(filter(str.isdigit, message))
                obj_id_int= int(obj_id_str)
            except ValueError:
                pause_time = 1
                print(f"[MOCK_STM.py]Invalid  command {message}")

            print(f"Pause command detected: {message}. Signaling main server to pause for OBJECT {obj_id_int}")
            # Send the pause time to the main server via the pause_queue
            self.pause_queue.put(obj_id_int)
            # Wait until the main server signals that pause is done
            self.pause_done_event.wait()
            self.pause_done_event.clear()
            print(f"Pause for OBJECT {obj_id_int}. Resuming command execution.")
            return  # Exit after handling pause

        if self.mock:
            print(f"[Mock Mode] Sent: {message}")
            self.stm_to_rpi_queue.put(message)
            # Simulate a response
            response = f"[Mock Mode] Response to {message}"
            # time.sleep(self.stm_buffer_time)
            print(f"[Mock Mode] Received: {response}")
        else:
            try:
                self.ser.write(message.encode('utf-8'))
                print(f"Sent: {message}")

                # Wait for a response with a short delay
                time.sleep(self.stm_buffer_time)  

                #send to android here
                
                response = self.ser.readline().decode('utf-8').strip()
                if response:
                    print(f"Received: {response}")
                else:
                    print("No response received")

            except Exception as e:
                print(f"Error sending command: {e}")

    def clear_commands(self):
        """Clear all commands in the queue."""
        with self.command_queue.mutex:
            self.command_queue.queue.clear()
        print("All commands cleared from the queue.")

    def run(self):
        """Thread's run method to continuously send commands."""
        self.connect()
        while self.running:
            self.send_next_command()
            
            # Optional: Add a small delay to prevent tight loop
            time.sleep(0.1)
        # self.disconnect()
        print("STM_Controller thread has been stopped.")

    def stop(self):
        """Stop the thread gracefully."""
        self.running = False

# Example usage
if __name__ == "__main__":
    # Create pause_queue and pause_done_event for handling pause commands
    pause_queue = queue.Queue()
    pause_done_event = threading.Event()

    # Function to handle pause signals from STM_Controller
    def pause_handler(pause_queue, pause_done_event):
        while True:
            try:
                # Wait for a pause time to be available
                pause_time = pause_queue.get(timeout=1)  # Adjust timeout as needed
                print(f"[Main Thread] Pausing for {pause_time} seconds...")
                time.sleep(pause_time)
                print(f"[Main Thread] Pause of {pause_time} seconds completed.")
                # Signal that the pause is done
                pause_done_event.set()
            except queue.Empty:
                # No pause signal received, continue
                # Check if controller_thread is still running
                if not controller_thread.is_alive() and pause_queue.empty():
                    break

    # Create an instance of the STM_Controller class
    controller_thread = STM_Controller(
        port='/dev/ttyUSB0',
        baud_rate=115200,
        pause_queue=pause_queue,
        pause_done_event=pause_done_event
    )

    # Start the STM_Controller thread
    controller_thread.start()

    commands = [
        'FW090', 'FR090', 'FW120', 'FL090', 'BW020', 'FL090', 'P___4',
    ]

    # Add the commands to the controller's queue
    controller_thread.add_commands(commands)

    # Start the pause_handler in a separate thread
    pause_thread = threading.Thread(target=pause_handler, args=(pause_queue, pause_done_event))
    pause_thread.start()

    # Function to monitor when all commands have been processed
    def monitor_commands(controller, pause_q, pause_done_evt):
        while True:
            # If the command queue is empty and there are no pending pauses, stop the controller
            if controller.command_queue.empty() and pause_q.empty():
                break
            time.sleep(0.5)

    # Start monitoring in the main thread
    try:
        monitor_commands(controller_thread, pause_queue, pause_done_event)
    except KeyboardInterrupt:
        print("Interrupted by user. Stopping controller...")
    finally:
        # Stop the STM_Controller thread gracefully
        controller_thread.stop()
        controller_thread.join()
        # Wait for the pause_handler to finish
        pause_thread.join()
        print("Controller has been stopped.")
