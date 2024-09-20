import serial
import queue
import os
import time
class SerialCommunicator:
    def __init__(self, serial_port, baud_rate, cmds):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.cmds = cmds
        self.command_queue = queue.Queue()
        self._prepare_commands()

    def _prepare_commands(self):
       
        for command in self.cmds['commands'].split(','):
            self.command_queue.put(command)

    def send_message(self):
       
        if not os.path.exists(self.serial_port):
            print(f"Serial port {self.serial_port} not found. Simulating message sending:")
            self._simulate_sending()
        else:
            try:
                # Open the serial connection
                with serial.Serial(self.serial_port, self.baud_rate, timeout=1) as ser:
                    while not self.command_queue.empty():
                        message = self.command_queue.get()

                        # Send the command
                        ser.write(message.encode('utf-8'))
                        print(f"Sent: {message}")

                        # Read the response
                        response = ser.readline().decode('utf-8').strip()
                        if response:
                            print(f"Received: {response}")
                        else:
                            print("No response received")
            except Exception as e:
                print(f"Error: {e}")

    def _simulate_sending(self):
        
        while not self.command_queue.empty():
            message = self.command_queue.get()
            time.sleep(0.5)
            print(f"Simulated sending: {message}")

# Example usage
if __name__ == "__main__":
    cmds = {'commands': 'SF090,RF090,SF120,LF090,SB020,LF090,P___4,SB020,LF090,SB030,RB090,SF030,P___6,SB030,RF090,SF020,LF090,SB010,RB090,LB090,RB090,SF020,P___2,SB040,RF090,P___5,SB020,LF090,SF030,LF090,SF030,RF090,P___3,SB010,LB090,SF010,RF090,P___1'}
    
    communicator = SerialCommunicator('/dev/ttyUSB0', 115200, cmds)
    communicator.send_message()
