import threading
import time
import os
import select#to handle rfcomm read blocking the thread from closing
class BluetoothComm:
    def __init__(self, rfcomm_device="/dev/rfcomm0", image_folder='/home/pi/test_rpi_server/image_results', channel=1):
        self.image_folder = image_folder

        #handling connections
        self.rfcomm_device = rfcomm_device
        self.channel = channel
        self.rfcomm = None
        self.sender_thread = None
        self.receiver_thread = None
        self.stop_event = threading.Event()  # Event to signal threads to stop
        self.isconnected =False
        self.forcestop=False
        

        #android
        self.stop_image_rec = True#by default stopImageRec
        self.android_info = None
        self.whichTask = ''
        self.start_time = None
        self.test_chat = False#flag set to false,then on top rpi_server will see this and use android.py send_message to send
        #handle retry,so if want start again,need clear coordinates:android_info


    def get_android_info(self):
        return self.android_info
    def set_android_info(self,decoded_data):
        self.android_info = decoded_data

    def open_rfcomm(self):
        try:
            self.rfcomm = open(self.rfcomm_device, "r+b", buffering=0)
            print(f"Opened RFCOMM device on {self.rfcomm_device}")
        except Exception as e:
            print(f"Error opening RFCOMM device: {e}")
            raise
    def send_message(self, message=None):
        try:
            if self.rfcomm is None:
                print("RFCOMM device is not open. Cannot send message.")
                return  

            if not message:
                message = 'test msg from rpi\n'  # Default message if none is provided
            else:
                message = '\n' + message + '\n'
            message = message.encode('utf-8')
            self.rfcomm.write(message)
            print(f"Sent: {message.decode('utf-8')}")
        except Exception as e:
            print(f"Error while sending: {e}")
            self.stop_event.set()
    def get_most_recent_image(self):
        try:
            files = [os.path.join(self.image_folder, f) for f in os.listdir(self.image_folder) if os.path.isfile(os.path.join(self.image_folder, f))]
            
            if not files:
                print("No image files found in the folder.")
                return None

            most_recent_file = max(files, key=os.path.getmtime)
            return most_recent_file
        except Exception as e:
            print(f"Error while fetching most recent image: {e}")
            return None
    def decide_data(self,decoded_data):
        if isinstance(decoded_data, str):
            #if string then task 1
            if decoded_data.strip().split('|')[0] == 'OBS':  
                
                print('task1')
                self.whichTask = 'task1'
                self.set_android_info(decoded_data.strip().split('|')[1:-1])
            if decoded_data.strip().split('|')[0] == 'STM':   
                print('task2')
                self.whichTask = 'task2'
                self.set_android_info(decoded_data.strip().split('|'))
    def process_data(self):
        return
    def receive_messages(self):
        
        while not self.stop_event.is_set():
            
            try:
                ready, _, _ = select.select([self.rfcomm], [], [], 1)
                if ready:
                    data = self.rfcomm.read(1024)
                    if data:
                        self.start_time = time.time() 
                        decoded_data = data.decode('utf-8')
                        print('============')
                        print(f'decoded data =={decoded_data}')
                        self.decide_data(decoded_data)     
                        print(f"Received: {self.android_info}")
                        
                        if decoded_data == 'stop49':
                            print('supposed to stop bluetooth connection')
                            self.stop_event.set()  # Signal both threads to stop
                        elif decoded_data.strip() == 'stopRec':
                            self.send_message('stopping image rec..')
                            self.stop_image_rec = True
                        elif decoded_data.strip() == 'startRec':
                            self.send_message('starting image rec..')
                            self.stop_image_rec = False
                        elif decoded_data.strip() == 'startChat':
                             self.test_chat = True
                             self.stop_image_rec = True#stop image_rec for cleaner terminal
                        elif decoded_data.strip() == 'stopChat':
                             print("stopping chat")
                             self.test_chat = False
                             self.stop_image_rec = False#stop image_rec for cleaner terminal
                        elif decoded_data.strip() == 'stopTask':
                            pass
                        

                else:
                    pass
        
            except Exception as e:
                if self.stop_event.is_set():
                    break  # Exit the loop if stop_event is set
                print(f"Error while receiving: {e}")
                self.stop_event.set()#notify other threads
                break
    
    def start(self):
        retry_delay = 5  

        while not self.stop_event.is_set():
            try:
                if self.forcestop:
                    print('halt trying to start bluetooth connection')
                    break

                self.open_rfcomm()  # Try to open the RFCOMM device
                self.stop_event.clear()  # Clear the stop signal if successful
                
                # Send the message once after connection is established
                self.send_message('test msg from rpi')

                self.receiver_thread = threading.Thread(target=self.receive_messages)
                self.receiver_thread.start()

                print("Bluetooth communication started successfully.")
                self.isconnected=True
                break  # Exit the loop if the connection is successful

            except Exception as e:
                print(f"Error starting Bluetooth communication: {e}\nRetrying in {retry_delay} seconds...")
                time.sleep(retry_delay)  # Wait before retrying

    def stop(self):
        self.send_message("stopping connection...")

        self.stop_event.set()  # Signal threads to stop
        

        if self.rfcomm:
            self.rfcomm.close()
            self.rfcomm = None 
            self.isconnected=False
            print(f"Closed RFCOMM device on {self.rfcomm_device}")

        if self.receiver_thread and self.receiver_thread.is_alive():
            self.receiver_thread.join(timeout=5)  # Wait up to 5 seconds to join the receiver thread
        if self.receiver_thread.is_alive():
            print("Receiver thread failed to exit in time.")



if __name__ == "__main__":
    bt_comm = BluetoothComm()

    try:
        bt_comm.start()

        # Main loop checks if stop_event is set
        while not bt_comm.stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        bt_comm.stop()
