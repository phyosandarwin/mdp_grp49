import requests
from find_device import get_master_ip
from image_handler import CameraHandler
from parse_image import decode_image
from android import BluetoothComm
import time
import os
import threading

def maintain_recent_images(folder, max_images):
    # Sort files based on creation time, oldest at the top
    images = sorted(os.listdir(folder), key=lambda x: os.path.getctime(os.path.join(folder, x)))
    
    # Check if there are more images than the max allowed
    if len(images) > max_images:
        # Remove the oldest images
        for image in images[:-max_images]:
            os.remove(os.path.join(folder, image))
            print(f"Removed {image} from {folder}")

def send_image_to_server(filename, url, bt_comm, retry_delay=5,retry_send_amount=5):
    retry_times = 0
    while retry_times < retry_send_amount:
        try:
            retry_times+=1
            with open(filename, 'rb') as img_file:
                files = {'file': img_file}
                response = requests.post(url, files=files)
                
                if response.status_code == 200:
                    json_response = response.json()
                    # Extract and print only 'boxes' and 'confidence' from the response
                    if 'boxes' in json_response and 'confidence' in json_response:
                        result_conf = json_response['confidence']
                        print(f"Image {filename} successfully sent to {url}")
                        print("Bounding Boxes:", json_response['boxes'])
                        print("Confidence Scores:", result_conf)
                        if 'class_name' in json_response:  # Send only when class name is identified
                            result_class_name = json_response['class_name']
                            print(f"class name = {result_class_name}")
                            print('---sending to android')
                            result_send = f'IMG-1-{result_class_name[0]}'
                            bt_comm.send_message(result_send)

                    if 'encoded_image' in json_response:
                        name_of_file = os.path.basename(filename)
                        decoded_filename = os.path.join(image_results_folder, f"{name_of_file}")
                        image_bytes = json_response['encoded_image']
                        decode_image(image_bytes, decoded_filename)
                        # Save decoded image to image_results folder
                        maintain_recent_images(image_results_folder, 3)
                    else:
                        print(f"Image {filename} successfully sent, but 'boxes' or 'confidence' not found in the response.")
                    
                    break  # Exit loop if successful
                
                else:
                    print(f"Failed to send image. Status code: {response.status_code}. Retrying in {retry_delay} seconds...")
        
        except requests.ConnectionError:
            print(f"___Connection error occurred while sending {filename}. Retrying in {retry_delay} seconds.{retry_times}/{retry_send_amount}")

        time.sleep(retry_delay)
if __name__ == "__main__":
    print('server started....\n')
    image_results_folder = 'image_results'
    images_folder = 'images'

    master_ip_address = get_master_ip()
    print(f'master ip address {master_ip_address}\n')
    url = f"http://{master_ip_address}:5055/predict"
    print(f'sending to {url} ')

    camera = CameraHandler(images_folder)

    os.makedirs(image_results_folder, exist_ok=True)


    bt_comm = BluetoothComm()
    # bt_comm.start()
    bluetooth_thread = threading.Thread(target=bt_comm.start)
    bluetooth_thread.start()
    captured_image_wait = 5
    while True:
        print('============')
        print('IMG RECOGNITION\n')
        filename = "captured_image.jpg"
        timestamp = time.strftime("%Y%m%d-%H%M%S")  # Format: YYYYMMDD-HHMMSS
        filename = f"captured_image_{timestamp}.jpg"
        
        if not bt_comm.stop_image_rec:
            filepath = camera.take_picture(filename)
            maintain_recent_images(images_folder,3)

            
            send_image_to_server(filepath, url, bt_comm)
        elif bt_comm.stop_image_rec:
            print('image rec paused...(send startRec on android to start)')
        
        print('============')
        time.sleep(captured_image_wait)

    camera.close()



#source venv/bin/activate