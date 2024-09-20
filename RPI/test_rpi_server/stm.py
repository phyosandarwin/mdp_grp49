import serial
import time
# Define the serial port and baud rate (make sure these match your STM32 setup)
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

def send_message():
    try:
        # Open the serial connection
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:

            message = "FW180"
            ser.write(message.encode('utf-8'))
            print(f"Sent: {message}")
            time.sleep(5)
           
            response = ser.readline().decode('utf-8').strip()
            if response:
                print(f"Received: {response}")
            else:
                print("No response received")
    except Exception as e:
        print(f"Error: {e}")

# Run the function to send the message
send_message()
