import serial
import queue
import time
# Define the serial port and baud rate (make sure these match your STM32 setup)
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

def send_message():
    try:
        # Open the serial connection
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            # cmds = {'commands': 'SF090,RF090,SF120,LF090,SB020,LF090,P___4,SB020,LF090,SB030,RB090,SF030,P___6,SB030,RF090,SF020,LF090,SB010,RB090,LB090,RB090,SF020,P___2,SB040,RF090,P___5,SB020,LF090,SF030,LF090,SF030,RF090,P___3,SB010,LB090,SF010,RF090,P___1'}
            # cmds = {'commands': 'FW050,BW050,ST000,TL070,FW010,RS050'}
            # cmds = {'commands': 'TL050,FW400'}
            # cmds = {'commands': 'FL90,FL90'}
            # cmds = {'commands': 'F002,FR20,F002'}
            # BRcmds = {'commands': 'F005,BR90,B005'}
            # cmds = {'commands': 'FW200,ST000'}
            # FR
            # cmds = {'commands': 'B010,FR90,B012'}
            # 30 20
            # FL
            cmds = {'commands': 'B030,F030,B030,FR05,FL050'}
            # 30 20
            # BL
            # cmds = {'commands':'F005,BL90,B005'}
            # 20 30
            # BR
            #cmds = {'commands': 'F013,BR90,B005'}
            # 30 30
            # cmds =  {'commands': 'F100,B100,F100,B100'}
            # cmds = {'commands': 'S   '}
            # Create a queue
            command_queue = queue.Queue()

            for command in cmds['commands'].split(','):
                command_queue.put(command)
            while not command_queue.empty():
                message = command_queue.get()
                time.sleep(3)
                ser.write(message.encode('utf-8'))
                print(f"Sent: {message}")

                response = None
                while response != 'ACK|':
                    response = ser.readline().decode('utf-8').strip()
                    print(response)
                if response:
                    print(f"Received: {response}")
                else:
                    print("No response received")
    except Exception as e:
        print(f"Error: {e}")

# Run the function to send the message
send_message()
