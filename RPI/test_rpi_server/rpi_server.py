import requests
from find_device import get_master_ip
from image_handler import CameraHandler
from parse_image import decode_image
from android import BluetoothComm
import time
import os
import threading
from config import Config
from p import process_strings#to format algo cmd for stm
from mock_stm import STM_Controller
import queue
import logging
import sys
import socket

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of log messages
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("rpi_server.log"),  # Log to a file
        logging.StreamHandler(sys.stdout)       # Also log to the console
    ]
)

class RPiServer:
    def __init__(self, image_folder=Config.IMAGE_FOLDER, results_folder=Config.RESULTS_FOLDER, max_images=Config.MAX_IMAGES, captured_image_wait=Config.CAPTURED_IMAGE_WAIT):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.image_folder = image_folder
        self.results_folder = results_folder
        self.max_images = max_images
        self.captured_image_wait = captured_image_wait
        self.movement_enabled = True # control robot movement


        # Initialize communication queues and events
        self.pause_queue = queue.Queue()
        self.pause_done_event = threading.Event()

        # Initialize folders
        os.makedirs(self.results_folder, exist_ok=True)

        self.camera_initialized = False  # Flag to track camera initialization
        try:
            self.camera = CameraHandler(self.image_folder)
            self.camera_initialized = True
            self.logger.info("Camera initialized successfully.")
        except Exception as e:
            self.camera = None
            self.camera_initialized = False
            self.logger.error(f"Failed to initialize camera: {e}")

        # # Initialize STM communication
        # self.stm_comm = STM_Controller(
        #     port='/dev/ttyUSB0',
        #     baud_rate=115200,
        #     pause_queue=self.pause_queue,
        #     pause_done_event=self.pause_done_event
        # )
        # self.stm_comm.start()  # Start the STM_Controller thread
        # Initialize Bluetooth communication
        self.bt_comm = BluetoothComm()

        # Get master IP address for server communication
        self.master_ip_address = get_master_ip()
        self.predict_url = f"http://{self.master_ip_address}:5055/predict"

        # self.algo_url = f"http://{self.master_ip_address}:5055/algo"
        self.algo_url = f"http://10.91.55.46:8001/"

        self.retry_delay=Config.RETRY_DELAY
        self.retry_send_max=Config.RETRY_SEND_MAX

        #tasks
        self.task_finshed = False

        # self.pause_handler_thread = threading.Thread(target=self.pause_handler, daemon=True)
        # self.pause_handler_thread.start()
        self.stm_comm = None
        self.pause_handler_thread = None

    def test_algo(self):
        SERVER_IP   = '10.96.49.24'
        PORT_NUMBER = 8001
        client_socket = socket(AF_INET, SOCK_DGRAM )
        client_socket.connect( (SERVER_IP, PORT_NUMBER) )
        
        client_socket.sendto('cool',(SERVER_IP,PORT_NUMBER))
        
    def pause_handler(self):
        """Handle pause signals from STM_Controller by executing image_rec."""
        while True:
            try:
                # Wait for a pause time to be available
                pause_time = self.pause_queue.get(timeout=1)  
                print(f"[Pause Handler] Received pause time: {pause_time} seconds.")
                
                # Execute image_rec
                self.image_rec()
                
                # Signal that the pause is done
                self.pause_done_event.set()
                print(f"[Pause Handler] Image recognition executed after pause.")
            except queue.Empty:
                # No pause signal received, continue
                if not self.stm_comm.is_alive() and self.pause_queue.empty():
                    break

    def maintain_recent_images(self, folder):
        """Maintain a maximum of self.max_images in the folder by removing the oldest ones."""
        images = sorted(os.listdir(folder), key=lambda x: os.path.getctime(os.path.join(folder, x)))
        if len(images) > self.max_images:
            for image in images[:-self.max_images]:
                os.remove(os.path.join(folder, image))
                print(f"Removed {image} from {folder}")

    def send_image_to_server(self, filename, mock=False):
        """Send the image to the server and handle the response."""
        retry_times = 0

        while retry_times < self.retry_send_max:
            try:
                retry_times += 1
                if mock:
                    # Simulate server response for mock image
                    print(f"Simulating sending mock image to {self.predict_url}")
                    mock_response = {
                        'boxes': [],
                        'confidence': [],
                        'class_name': 'MockClass'
                    }
                    self.process_server_response(mock_response, filename)
                    break  # Exit loop if successful
                else:
                    with open(filename, 'rb') as img_file:
                        print(f"sending to {self.predict_url}")
                        files = {'file': img_file}
                        response = requests.post(self.predict_url, files=files)

                        if response.status_code == 200:
                            json_response = response.json()
                            self.process_server_response(json_response, filename)
                            break  # Exit loop if successful

                        else:
                            print(f"Failed to send image. Status code: {response.status_code}. Retrying in {self.retry_delay} seconds...")

            except requests.ConnectionError:
                print(f"Connection error occurred while sending {filename}. Retrying in {self.retry_delay} seconds... {retry_times}/{self.retry_send_max}")

            time.sleep(self.retry_delay)


    def process_server_response(self, json_response, filename):
        """Process the server response and send relevant information via Bluetooth."""
        if 'boxes' in json_response and 'confidence' in json_response:
            #
            result_conf = json_response['confidence']
            print(f"Image {filename} successfully sent to {self.predict_url}")
            print("Bounding Boxes:", json_response['boxes'])
            print("Confidence Scores:", result_conf)

            if 'class_name' in json_response:  # Send only when class name is identified
                result_class_name = json_response['class_name']
                print(f"class name = {result_class_name}")
                result_send = f'IMG-1-{result_class_name}'#unhardcode this
                self.bt_comm.send_message(result_send)

        # if 'encoded_image' in json_response:
        #     name_of_file = os.path.basename(filename)
        #     decoded_filename = os.path.join(self.results_folder, f"{name_of_file}")
        #     image_bytes = json_response['encoded_image']
        #     decode_image(image_bytes, decoded_filename)
        #     self.maintain_recent_images(self.results_folder)
        else:
            print(f"Plain Image {filename}successfully sent, but 'boxes' or 'confidence' not found in the response.")

    def start_bluetooth(self):
        """Start Bluetooth communication in a separate thread."""
        bluetooth_thread = threading.Thread(target=self.bt_comm.start)
        bluetooth_thread.start()
        self.bluetooth_thread = bluetooth_thread
    def stop_bluetooth(self):
        if self.bluetooth_thread:
            print('closing bluetooth thread..')
            if self.bt_comm.isconnected:
                print('bluetooth conencted,now stopping conenction')
                self.bt_comm.stop()  #  stop Bluetooth communication
            self.bluetooth_thread.join()  # Wait for the Bluetooth thread to finish
            print("Bluetooth thread stopped.")
    
    def image_rec(self):
        """Handle image capture and recognition."""
        print('============')
        print('IMG RECOGNITION\n')

        # Check if camera is initialized
        if self.camera_initialized and self.camera is not None:
            # Generate the filename for the captured image
            filename = f"captured_image_{time.strftime('%Y%m%d-%H%M%S')}.jpg"
            print(f"Capturing image: {filename}")

            # Check if image recognition is paused
            if not self.bt_comm.stop_image_rec:
                try:
                    # Capture image
                    filepath = self.camera.take_picture(filename)
                    print(f"Image captured at {filepath}")

                    # Maintain a fixed number of recent images
                    self.maintain_recent_images(self.image_folder)

                    # Send the image to the server
                    self.send_image_to_server(filepath)
                except Exception as e:
                    print(f"Error during image capture: {e}")
            else:
                print('Image recognition paused...(send startRec on Android to start)')
        else:
            # Mock run when camera is not initialized
            print('Camera not initialized. Performing mock image recognition.')

            # Simulate image capture
            mock_filename = "mock_captured_image.jpg"
            mock_filepath = os.path.join(self.image_folder, mock_filename)
            print(f"Simulating image capture: {mock_filepath}")

            # Maintain a fixed number of recent images
            self.maintain_recent_images(self.image_folder)

            # Simulate sending image to server
            self.send_image_to_server(mock_filepath, mock=True)

            # Optionally, simulate waiting time
            time.sleep(self.captured_image_wait)

        print('============')
    def process_android_data_for_algo(self,android_data,category="category",mode="0"):
        processed_data = []

        for obstacles in android_data:
            temp = {}
            each_obs = obstacles.split(',')
            temp["x"] = each_obs[0]
            temp["y"] = each_obs[1]
            temp["id"] = each_obs[3]
            direction =  each_obs[2]
            # temp["d"] = obstacles[3]#direction
            if direction == 'N':
                temp["d"] = 0
            if direction == 'E':
                temp["d"] =2
            if direction == 'S':
                temp["d"] = 4
            if direction == 'W':
                temp["d"] = 6
            
            processed_data.append(temp)
        payload = {
            "cat":category,
            "value":processed_data,
            "mode":mode
        }
        return payload
    def start_stm(self,commands):
        # Initialize STM communication
        self.stm_comm = STM_Controller(
            port='/dev/ttyUSB0',
            baud_rate=115200,
            pause_queue=self.pause_queue,
            pause_done_event=self.pause_done_event
        )
        self.stm_comm.start()  # Start the STM_Controller thread
        print("STM_Controller thread started.")

        self.stm_comm.add_commands(commands)

        self.pause_handler_thread = threading.Thread(target=self.pause_handler, daemon=True)
        self.pause_handler_thread.start()

        #must add this to join back so TASK 1 can continue down
        self.pause_handler_thread.join()
        print("Pause handler thread completed.")

        # Now, join the STM_Controller thread to ensure it has finished processing commands
        self.stm_comm.join()
        print("STM_Controller thread completed.")   

    def task_1(self):
        print('task 1 start...setting task_finish to false')
        self.task_finshed = False
        android_data = self.bt_comm.android_info
        processed_android_data = self.process_android_data_for_algo(android_data)
        print('Android:',processed_android_data)
        self.logger.info(f"processed_android_data sent to algo :{processed_android_data} at {self.algo_url}")
        response_algo = requests.post(self.algo_url, json={"data": android_data})
        #use algo send to stm
        robot_commands = response_algo.json()['commands']#just take the 'commands key
        formatted_cmds  = process_strings(robot_commands.split(','))
        
        print(f"response from algo{formatted_cmds}")
        self.logger.info(f"response from algo{formatted_cmds}")

        print('===running stm=====')
        self.start_stm(formatted_cmds)

        #send message here to android to tell it now then start the clock
        # while True:
        #     self.image_rec()
        #send coord to algo

        #algo send to stm


        end= time.time()
        duration = end - self.bt_comm.start_time

        print(f'task 1 finished in {duration}')#got some delay from the moment it receives start to this point
        self.bt_comm.whichTask = ''
        self.android_info = None
        self.task_finshed = True
        return
    def task_2(self):
        print('task 2 start...setting task_finish to false')
        self.task_finshed = False
        time.sleep(5)

        print('task 2 finished')
        self.bt_comm.whichTask = ''
        self.android_info = None
        self.task_finshed = True
        return
    def run(self):
        """Main server loop that captures images and sends them to the server."""
        print('RPi server started...')
        print(f'Master IP address: {self.master_ip_address}')
        print(f'Sending images to {self.predict_url}')

        self.start_bluetooth()

        try:
            while True:
                if not self.camera_initialized:
                    print('Camera not connected. Connect Camera to RPI...')
                if not self.bt_comm.isconnected:
                    print('Bluetooth not connected. Connect to Android...')
                    time.sleep(2)  # Wait before checking again
                    continue  # Skip the rest of the loop if not connected

                print('Bluetooth connected!')
                while self.bt_comm.isconnected:  # Keep processing as long as Bluetooth is connected
                    
                    if self.bt_comm.whichTask == 'task1':#means received message from Android liao
                        #send to PC server
                        self.task_1()
                        print('waiting for next instruction(task 1 or task 2)...')
                    if self.bt_comm.whichTask == 'task2':
                        self.task_2()
                        print('waiting for next instruction(task 1 or task 2)...')
                    elif not self.bt_comm.stop_image_rec:
                        print('waiting for start signal from android')
                        self.image_rec()
                   
                    
                # If Bluetooth gets disconnected, loop back to check for connection
                print('Bluetooth disconnected. Waiting for reconnection...')

        except KeyboardInterrupt:
            print("Shutting down RPiServer...")
            self.bt_comm.forcestop=True#so stop retrying connection in start()

        finally:
          
            self.stop_bluetooth()
            if self.camera_initialized:
                self.camera.close()
             # Stop the STM_Controller thread
            if self.stm_comm:
                self.stm_comm.stop()
                self.stm_comm.join()
            # Wait for the pause_handler thread to finish
                self.pause_handler_thread.join()
            print("RPiServer stopped.")


if __name__ == "__main__":
    # Instantiate and run the RPi server
    server = RPiServer()
    server.run()
