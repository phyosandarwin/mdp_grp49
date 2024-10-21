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
from algo_handler import AlgoHandler
import json
from collections import Counter
import glob
#48:61:EE:2A:AA:04
os.makedirs('logs', exist_ok=True)
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of log messages
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("./logs/rpi_server.log"),  # Log to a file
        # logging.StreamHandler(sys.stdout)       # Also log to the console
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

        self.stop_event = threading.Event()
        self.stm_to_rpi_queue = queue.Queue()#queue to notify andorid of the commands sent

        self.clear_log_files()

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
            # self.logger.error(f"Failed to initialize camera: {e}")
        # Initialize Bluetooth communication
        self.bt_comm = BluetoothComm()

        # Get master IP address for server communication
        self.master_ip_address = get_master_ip()
        self.predict_url = f"http://{self.master_ip_address}:5055/predict"

        self.algo_url = f"http://{self.master_ip_address}:5055/algo"#just for testing sending


        self.retry_delay=Config.RETRY_DELAY
        self.retry_send_max=Config.RETRY_SEND_MAX

        #tasks
        self.task_finshed = False
        # self.pause_handler_thread = threading.Thread(target=self.pause_handler, daemon=True)
        # self.pause_handler_thread.start()
        self.stm_comm = None
        self.pause_handler_thread = None

        # Initialize algo handler
        self.algo_handler = AlgoHandler()
        
        # Start the AlgoHandler server in a separate thread and store it as an instance variable
        self.algo_thread = threading.Thread(target=self.algo_handler.start_server, daemon=True)
        self.algo_thread.start()
        self.logger.info("AlgoHandler server thread started.")

        # Create separate logger for image_rec()
        self.image_rec_logger = logging.getLogger(f"{self.__class__.__name__}.image_rec")
        self.image_rec_logger.setLevel(logging.DEBUG)
        image_rec_handler = logging.FileHandler("./logs/image_rec.log")
        image_rec_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        image_rec_handler.setFormatter(image_rec_formatter)
        self.image_rec_logger.addHandler(image_rec_handler)
        self.image_rec_logger.propagate = False  # Prevent logging from propagating to the main logger

        # Create separate logger for task_1()
        self.task1_logger = logging.getLogger(f"{self.__class__.__name__}.task1")
        self.task1_logger.setLevel(logging.DEBUG)
        task1_handler = logging.FileHandler("./logs/task1.log")
        task1_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        task1_handler.setFormatter(task1_formatter)
        self.task1_logger.addHandler(task1_handler)
        self.task1_logger.propagate = False  # Prevent logging from propagating to the main logger

        # Create separate logger for task_2()
        self.task2_logger = logging.getLogger(f"{self.__class__.__name__}.task2")
        self.task2_logger.setLevel(logging.DEBUG)
        task2_handler = logging.FileHandler("./logs/task2.log")
        task2_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        task2_handler.setFormatter(task2_formatter)
        self.task2_logger.addHandler(task2_handler)
        self.task2_logger.propagate = False  # Prevent logging from propagating to the main logger

        self.predict_image_result = None


        images_path = '/home/pi/test_rpi_server_2/mdp_grp49/RPI/test_rpi_server/images'
        files = glob.glob(os.path.join(images_path,'*'))

        for file in files:
            try:
                os.remove(file)
                print(f"Deleted{file}")
            except Exception as e:
                print(e)

    def clear_log_files(self):
        """Clear the contents of all log files during initialization."""
        log_files = [
            "./logs/rpi_server.log",
            "./logs/image_rec.log",
            "./logs/task1.log"
        ]
        
        for log_file in log_files:
            try:
                # Truncate the file (clear contents)
                open(log_file, 'w').close()
                print(f"Cleared log file: {log_file}")
            except FileNotFoundError:
                print(f"Log file not found, skipping: {log_file}")
    def monitor_stm_queue(self):
        while not self.stop_event.is_set():
            try:
                message = self.stm_to_rpi_queue.get(timeout=1)
                print('THREAD FOR SENDING MSG TO ANDROID')
                print(f"Received from STM: {message}")
                # Process the message as needed
                # For example, send it to Android via Bluetooth
                # self.bt_comm.send_message(message)
            except queue.Empty:
                # No message received in this interval
                pass
        print("monitor_stm_queue thread exiting.")
        
    def pause_handler(self):
        while not self.stop_event.is_set():
            try:
                pause_time = self.stm_comm.pause_time
                # Wait for a pause time to be available
                obj_id_int = self.pause_queue.get(timeout=1)  
                print(f"[Pause Handler][RPI_SERVER] || OBJECT : {obj_id_int} for {pause_time}")
                self.bt_comm.stop_image_rec=False
                # Execute image_rec
                self.image_rec(obj_id_int)
                self.bt_comm.stop_image_rec=True
                print("[Pause Handler]setting self.bt_comm.stop_image_rec back to True")
                
                # Signal that the pause is done
                self.pause_done_event.set()
                print(f"[Pause Handler] Image recognition executed after pause.")
            except queue.Empty:
                # No pause signal received, continue
                if not self.stm_comm.is_alive() and self.pause_queue.empty():
                    break
        print("pause_handler thread exiting.")

    def maintain_recent_images(self, folder):
        """Maintain a maximum of self.max_images in the folder by removing the oldest ones."""
        images = sorted(os.listdir(folder), key=lambda x: os.path.getctime(os.path.join(folder, x)))
        if len(images) > self.max_images:
            for image in images[:-self.max_images]:
                os.remove(os.path.join(folder, image))
                # print(f"Removed {image} from {folder}")
                self.image_rec_logger.debug(f"Removed {image} from {folder}")

    def post_image_to_server(self, filename, mock=False,obj_id_int=None):
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
                        'class_ids': 'MockClass'
                    }
                    self.process_server_response(mock_response, filename, obj_id_int)
                    break  # Exit loop if successful
                else:
                    with open(filename, 'rb') as img_file:
                        # Example of the additional JSON payload
                        payload = {
                            'request_id': obj_id_int,  # Replace with actual data if needed
                            'additional_info': 'Sample information'  # Example JSON body
                        }

                        # Log that the request is being sent
                        self.image_rec_logger.debug(f"sending to {self.predict_url}")

                        # Sending both the image file and the JSON payload
                        files = {'file': img_file}
                        # Flatten the JSON data for the form-data structure
                        data = {key: str(value) for key, value in payload.items()}

                        _ = requests.post(self.predict_url, files=files, data=data)
                        return

                        if response.status_code == 200:
                            json_response = response.json()
                            self.process_server_response(json_response, filename , obj_id_int)
                            break  # Exit loop if successful
                        else:
                            print(f"Failed to send image. Status code: {response.status_code}. Retrying in {self.retry_delay} seconds...")

            except requests.ConnectionError:
                response = requests.post(f"http://{self.master_ip_address}:5055/status")
                print("response from flask",response)
                print(f"Connection error occurred while sending {filename}. Retrying in {self.retry_delay} seconds... {retry_times}/{self.retry_send_max}")

            time.sleep(self.retry_delay)

    def send_image_to_server(self, filename, mock=False,obj_id_int=None):
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
                        'class_ids': 'MockClass'
                    }
                    self.process_server_response(mock_response, filename, obj_id_int)
                    break  # Exit loop if successful
                else:
                    with open(filename, 'rb') as img_file:
                        # Example of the additional JSON payload
                        payload = {
                            'request_id': obj_id_int,  # Replace with actual data if needed
                            'additional_info': 'Sample information'  # Example JSON body
                        }

                        # Log that the request is being sent
                        self.image_rec_logger.debug(f"sending to {self.predict_url}")

                        # Sending both the image file and the JSON payload
                        files = {'file': img_file}
                        # Flatten the JSON data for the form-data structure
                        data = {key: str(value) for key, value in payload.items()}

    #                    _ = requests.post(self.predict_url, files=files, data=data)
    #                    return
                        response = requests.post(self.predict_url, files=files, data=data)

                        if response.status_code == 200:
                            json_response = response.json()
                            self.process_server_response(json_response, filename , obj_id_int)
                            break  # Exit loop if successful
                        else:
                            print(f"Failed to send image. Status code: {response.status_code}. Retrying in {self.retry_delay} seconds...")

            except requests.ConnectionError:
                response = requests.post(f"http://{self.master_ip_address}:5055/status")
                print("response from flask",response)
                print(f"Connection error occurred while sending {filename}. Retrying in {self.retry_delay} seconds... {retry_times}/{self.retry_send_max}")

            time.sleep(self.retry_delay)

    def process_server_response(self, json_response, filename,obj_id_int=None):
        """Process the server response and send relevant information via Bluetooth."""
        if 'boxes' in json_response and 'confidence' in json_response:
            #
            result_conf = json_response['confidence']
            # print(f"Image {filename} successfully sent to {self.predict_url}")
            # print("Bounding Boxes:", json_response['boxes'])
            # print("Confidence Scores:", result_conf)
            self.image_rec_logger.debug(f"Image {filename} successfully sent to {self.predict_url}")
            self.image_rec_logger.debug(f"Bounding Boxes:{json_response['boxes']}")
            self.image_rec_logger.debug(f"Confidence Scores:{result_conf}")
            print("JSON RESPONSE", json_response)
            print("None type", )
            if 'class_ids' in json_response:  # Send only when class name is identified
                result_class_name = json_response['class_ids'][0]#get first prediction
                self.predict_image_result = result_class_name
                # print(f"class name = {result_class_name}")
                result_send = f'IMG-{obj_id_int}-{result_class_name}'
                self.image_rec_logger.debug(result_send)
                if obj_id_int is None:
                    print('result_send is]]]')
                    print(result_send)
                    if result_class_name == 10:
                         pass
                else:
                    print(f"=====SENDING IMAGE PREDICITON TO ANDROID{result_send}=====")
                    if result_class_name == 10:
                         pass
                    else:
                        self.bt_comm.send_message(result_send)
        else:
            print("NO CLASS ID IN RESULT SEND")
            # print(f"Plain Image {filename}successfully sent, but 'boxes' or 'confidence' not found in the response.")
            self.image_rec_logger.debug(f"Plain Image {filename}successfully sent, but 'boxes' or 'confidence' not found in the response.")
            self.bt_comm.send_message(f"image taken no bounding boxes found for {obj_id_int}")
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
    
    def image_rec(self,obj_id_int=None):
        """Handle image capture and recognition."""
        print('============')
        print('IMG RECOGNITION\n')

        self.image_rec_logger.debug('============')
        self.image_rec_logger.debug('IMG RECOGNITION\n')

        # Check if camera is initialized
        if self.camera_initialized and self.camera is not None:
            # Generate the filename for the captured image
            filename = f"obj_{obj_id_int}_{time.strftime('%H%M%S')}.jpg"
            # print(f"Capturing image: {filename}")
            self.image_rec_logger.debug(f"Capturing image: {filename}")
            # self.bt_comm.send_message(f"image taken for {obj_id_int}")

            # Check if image recognition is paused
            if not self.bt_comm.stop_image_rec:
                try:
                    # Capture image
                    filepath = self.camera.take_picture(filename)
                    print(f"Image captured at {filepath}")
                    self.image_rec_logger.debug(f"Image captured at {filepath}")

                    self.send_image_to_server(filepath,mock=False,obj_id_int = obj_id_int)

                    # Maintain a fixed number of recent images
                    self.maintain_recent_images(self.image_folder)
                except Exception as e:
                    print(f"Error during image capture: {e} {self.master_ip_address}")
                    self.image_rec_logger.error(f"Error during image capture: {e}")
            else:
                print('Image recognition paused...(send startRec on Android to start)')
                self.image_rec_logger.info('Image recognition paused...(send startRec on Android to start)')
        else:
            # Mock run when camera is not initialized
            self.image_rec_logger.info('Camera not initialized. Performing mock image recognition.')
            print('Camera not initialized. Performing mock image recognition.')

            # Simulate image capture
            mock_filename = "mock_captured_image.jpg"
            mock_filepath = os.path.join(self.image_folder, mock_filename)
            print(f"Simulating image capture: {mock_filepath}")
            self.image_rec_logger.debug(f"Simulating image capture: {mock_filepath}")

            # Maintain a fixed number of recent images
            self.maintain_recent_images(self.image_folder)

            # Simulate sending image to server
            self.send_image_to_server(mock_filepath, mock=True,obj_id_int = obj_id_int)

            # Optionally, simulate waiting time
            time.sleep(self.captured_image_wait)
    
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
    
    def start_stm(self):
        # Initialize STM communication
        self.stm_comm = STM_Controller(
            port='/dev/ttyUSB0',
            baud_rate=115200,
            pause_queue=self.pause_queue,
            pause_done_event=self.pause_done_event,
            stm_to_rpi_queue=self.stm_to_rpi_queue 
        )
        # self.stm_comm.start()  # Start the STM_Controller thread
        # print("STM_Controller thread started.")
        self.stm_comm.connect()
        # self.stm_comm.add_commands(commands,send_coords)

        # self.pause_handler_thread = threading.Thread(target=self.pause_handler, daemon=True)
        # self.pause_handler_thread.start()

        # #must add this to join back so TASK 1 can continue down
        # self.pause_handler_thread.join()
        # print("Pause handler thread completed.")

        # # Now, join the STM_Controller thread to ensure it has finished processing commands
        # self.stm_comm.join()
        # print("STM_Controller thread completed.")   
    
    def task_1(self):
        self.bt_comm.stop_image_rec=False
        print('task 1 start...setting task_finish to false')
        self.task_finshed = False
        android_data = self.bt_comm.android_info
        self.task1_logger.debug(f'Android data: {android_data}')
        # processed_android_data = self.process_android_data_for_algo(android_data)
        print('Android:',android_data,type(android_data[0]))
        for i in range(len(android_data)):
            first = android_data[i].split(",")
            first[0] = str(int(first[0])-1)
            first[1] = str(int(first[1])-1)
            android_data[i] = ",".join(first)

        print('Android:',android_data)
        # android_data_str = """{}""".format("\n".join(android_data))
        # print(android_data_str)
        # self.task1_logger.debug(f'Android data string:\n{android_data_str}')
    
        # #just for testing sending of messages
        # response_algo = requests.post(self.algo_url, json={"data": android_data})
        # robot_commands = response_algo.json()['commands']#just take the 'commands key
        # formatted_cmds  = process_strings(robot_commands.split(','))
        
        # # print(f"response from algo{formatted_cmds}")
        # self.logger.info(f"response from algo{formatted_cmds}")

        # print('===running stm=====')
        # self.start_stm(formatted_cmds)
        if self.algo_handler.conn:
            print("CONNECTION WITH ALGO'S SOCKET")
        # requests.post(self.algo_url,android_data)
        #hardcode here first try
        # message = """{"cat":"obstacles","value":{"obstacles":[{"x":7,"y":14,"id":1,"d":0},{"x":15,"y":8,"id":2,"d":6},{"x":4,"y":3,"id":3,"d":2},{"x":9,"y":7,"id":4,"d":4}],"mode":"0"}}"""
        #dont proceed until connected to algo computer
        while not self.algo_handler.conn:
            print(f"CONNECT TO ALGO COMPUTER server ip:{self.algo_handler.host}/{self.algo_handler.port}")
            self.task1_logger.debug("Waiting for AlgoHandler to connect.")
            # print("change port:")
            # new_port = input("new_port:")
            # self.algo_handler.port = new_port
            time.sleep(10)
            
        message = android_data
        try:
            print(type(message))
        except Exception as e:
            print(e)
        
        self.algo_handler.send_external_message(message)
        self.task1_logger.debug(f"Sent message to AlgoHandler: {message}")
        print(f"Sent message to AlgoHandler: {message}")

        # Receive a message
        received_message = self.algo_handler.receive_message()
        self.image_rec_logger.debug(received_message)

        # Handle the received message
        while not received_message:
            print(f'waiting for response from algo{received_message}')
            #time.sleep(5)#give some buffer for algo to compute
            received_message = self.algo_handler.receive_message()
            #time.sleep(3)
            self.algo_handler.send_external_message(message)
        
        try:
            print("RECEIVED MESSAGE")
            print(received_message)
            received_data = json.loads(received_message)
            print("Parsed received data:", received_data)

            self.task1_logger.debug(f"Parsed received data: {received_data}")
        except json.JSONDecodeError:
            print("Error decoding received JSON.")
            self.task1_logger.error("Error decoding received JSON.")

        # Close the connection after communication
        # self.algo_handler.close_connection()

        # response_algo = requests.post(self.algo_url, json={"data": android_data})
        #use algo send to stm
        # robot_commands = response_algo.json()['commands']#just take the 'commands key
        robot_commands = received_data['value']['commands']
        # car_coords = received_data['value']['coords']
        # car_coords = None
        print("======")
        #print(car_coords)
        send_coords = []
        print(self.stm_to_rpi_queue)
        
        #for coord in car_coords:
            # self.bt_comm.send_message(",".join(car_coords[i]))
         #   send = "UPDATE-" + str(int(coord[0]/10)+1) +  '-' + str(int(coord[1]/10)+1) +  '-' + coord[2]
            # self.bt_comm.send_message(send)
          #  send_coords.append(send)
            # time.sleep(1)
            
        formatted_cmds  = process_strings(robot_commands.split(','))
        print(f"response from algo{formatted_cmds}")
        self.logger.info(f"response from algo{formatted_cmds}")

        print('===running stm=====')
        self.start_stm()
        try:
            self.stm_comm.add_commands(formatted_cmds,send_coords)
        except Exception as e:
            print(e)

        i = 0
        first_command = self.stm_comm.command_queue.get()
        if first_command.startswith('P_'):
            obj_id_str = ''.join(filter(str.isdigit, first_command))
            print('OBJ-ID_STR')
            print(obj_id_str)
            try:
                obj_id_int= int(obj_id_str)
            except Exception as e:
                obj_id_int= int(obj_id_str)
                print(obj_id_str)
                print(e)

            self.image_rec(obj_id_int)
        else:
            res= self.stm_comm.send_next_command(first_command).split('|')[0]
        
        count = 0
        while not self.stm_comm.command_queue.empty():
            if res == 'ACK':
                stm_command = self.stm_comm.command_queue.get()
                print('STM_COMMAND')
                print(stm_command)
                # Case 1: Pause Command (Take photo)
                if stm_command.startswith('P_'):  # Pause command
                    # Extract the pause time; assuming format 'P___<number>'
                    obj_id_str = ''.join(filter(str.isdigit, stm_command))
                    print('OBJ-ID_STR')
                    print(obj_id_str)
                    try:
                        obj_id_int= int(obj_id_str)
                    except Exception as e:
                        obj_id_int= int(obj_id_str)
                        print(obj_id_str)
                        print(e)

                    self.image_rec(obj_id_int)#keeps taking,and when its time to take for obstacle pass in  obj id
                    #time.sleep(1)
                else:
                    # add part on changing sleep time according to what previous turn was it 
                    #stm command['F020', 'FR20', 'F010', 'P___0', 'B030', 'FR20', 'B020', 'BL20', 'FL20', 'F020', 'P___0']
                    # time.sleep(1)
                    res = self.stm_comm.send_next_command(stm_command).split('|')[0]

                    
            else:
                continue

        end= time.time()
        duration = end - self.bt_comm.start_time
        self.bt_comm.send_message('ENDED')
        print(f'task 1 finished in {duration}')#got some delay from the moment it receives start to this point
        self.bt_comm.whichTask = ''
        self.android_info = None
        self.task_finshed = True
        self.bt_comm.stop_image_rec=True
        return
    
    def task_2(self):
        response = self.stm_comm.send_next_command('S   ')
        print('task 2 start...setting task_finish to false')
        self.task_finshed = False
        # count = 0
        count_2=0
        while True:
            while response != "A":
                response = self.stm_comm.ser.readline().decode('utf-8').strip()
                if count_2 > 4:
                    print("breaking out of loop")
                    break
                print(response)
                print("count 2:")
                print(count_2)
                count_2+=1
            if count_2 > 4:
                self.bt_comm.stop_image_rec=True
                break
            self.bt_comm.stop_image_rec=False
            self.image_rec(None)
            self.bt_comm.stop_image_rec=True
            # count +=1
            print(self.predict_image_result)
            if self.predict_image_result:
                final_result = int(self.predict_image_result)
                print('====')
                print(final_result)
                if final_result == 39:
                    print('++++=')
                    response = self.stm_comm.send_next_command('L   ')
                    self.task2_logger.info(response)
                    # response="AA"
                elif final_result == 38:
                    response = self.stm_comm.send_next_command('R   ')
                    self.task2_logger.info(response)
                    # response="AA"
                

                # time.sleep(5)
                # self.predict_image_result[0] = None#reset if not will send prev one
            
        # final_result = Counter(results_store).most_common(1)
        # self.stm_comm.send_next_command(final_result)
        # print(results_store)
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

        # Start monitoring STM to RPi queue
        # print("staring STM_TO_RPI QUEUE THREAD")
        # self.stm_monitor_thread = threading.Thread(target=self.monitor_stm_queue, daemon=True)
        # self.stm_monitor_thread.start()

        self.start_bluetooth()
        self.start_stm()
        # self.bt_comm.whichTask = 'task2'
        self.bt_comm.stop_image_rec = True
        try:
            while not self.stop_event.is_set():
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
                    elif self.bt_comm.whichTask == 'task2':
                        self.task_2()
                        print('waiting for next instruction(task 1 or task 2)...')
                    elif not self.bt_comm.stop_image_rec:
                        # print('waiting for start signal from android')
                        self.image_rec()
                        time.sleep(5)
                    
                    elif self.bt_comm.stop_image_rec and self.bt_comm.test_chat:
                        print("===CHAT ENABLED===")
                        msg_to_android = input("Enter message:")
                        self.bt_comm.send_message(msg_to_android)          
                    
                # If Bluetooth gets disconnected, loop back to check for connection
                print('Bluetooth disconnected. Waiting for reconnection...')

        except KeyboardInterrupt:
            print("Shutting down RPiServer...")
            self.stop_event.set()
            self.bt_comm.forcestop=True#so stop retrying connection in start()

        finally:
            self.algo_handler.stop_server()   # Signal the AlgoHandler to stop

            # Close AlgoHandler connection
            if self.algo_thread.is_alive():
                self.algo_thread.join()  # Wait for the AlgoHandler thread to finish
                print("AlgoHandler thread stopped.")
            
            
            self.stop_bluetooth()
            if self.camera_initialized:
                self.camera.close()
             # Stop the STM_Controller thread
            if self.stm_comm:
                self.stm_comm.stop()
                # self.stm_comm.join()
            # Wait for the pause_handler thread to finish
                # self.pause_handler_thread.join()
            # if self.stm_monitor_thread:
            #     self.stm_monitor_thread.join()
            print("RPiServer stopped.")


if __name__ == "__main__":
    # Instantiate and run the RPi server
    server = RPiServer()
    server.run()
