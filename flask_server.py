import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from model import yolo_model
from image_handler import get_encoded_image
from try_socket import SimpleSocketClient
from algo import Algo
import logging
app = Flask(__name__)
CORS(app)

app.logger.setLevel(logging.DEBUG)

UPLOAD_FOLDER = 'object_upload_final'

RESULT_FOLDER='object_results_final'
JSON_FOLDER='json_results'
MAX_IMAGES = 10
model_handler = None


# socket_server_ip = "10.96.49.30"
# socket_server_port = 8001

# # Instantiate the SimpleSocketClient
# socket_client = SimpleSocketClient(socket_server_ip, socket_server_port)


os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def remove_file(folder, filename):
    file_path = os.path.join(folder, filename)
    
    # Check if the file exists
    if os.path.exists(file_path):
        os.remove(file_path)  # Remove the file
        print(f"File {filename} has been removed.")
    else:
        print(f"File {filename} not found in {folder}.")


def print_debug():
    print("==================================================================================")
    print(f"==================Response status of current request===↓========================")

def maintain_recent_images(folder, max_images):
    # Sort files based on creation time, oldest at the top
    images = sorted(os.listdir(folder), key=lambda x: os.path.getctime(os.path.join(folder, x)))
    
    # Check if there are more images than the max allowed
    if len(images) > max_images:
        # Remove the oldest images
        for image in images[:-max_images]:
            os.remove(os.path.join(folder, image))
            print(f"Removed {image} from {folder}")

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['file']
    request_id = request.form.get('request_id')
    folder_name = 'obj_' + str(request_id)
    print('folder_name',folder_name)
    additional_info = request.form.get('additional_info')
    print("================== RECEIVED DATA =====================", flush=True)
    print(f"OBJCET ID: {request_id} ||", flush=True)
    obj_results_path = os.path.join('./object_results_final',f'obj_{request_id}')
    obj_upload_path = os.path.join('./object_upload_final',f'obj_{request_id}')
    os.makedirs(obj_results_path, exist_ok=True)
    os.makedirs(obj_upload_path, exist_ok=True)
    global model_handler
    
    if file:
        filename = file.filename
        file_path = os.path.join(obj_upload_path, filename)
        

        file.save(file_path)
        print(f"FILEPATH {file_path}")
        #so just chnage RESULT FOLDER TO BECOME THE distinct folder here
        maintain_recent_images(os.path.join(UPLOAD_FOLDER,folder_name), MAX_IMAGES )
        print(f"FILENAME{filename}")
        result,bounding_box_flag = model_handler.run_inference(filename,folder_name)
        if bounding_box_flag:#means got save into results folder
            result_image_filepath = obj_results_path
            # encoded_image= get_encoded_image(result_image_filepath)

            # result['encoded_image'] = encoded_image
            maintain_recent_images(obj_results_path, MAX_IMAGES )
            print_debug()
            return jsonify(result), 200
        else:
            print_debug()
            return jsonify(result), 200
        
        
    else:
        return jsonify({"error": "No image received."}), 400


@app.route('/algo', methods=['POST'])
def algo_receive():
    pass


@app.route('/status', methods=['GET'])
def status():
    return jsonify({"result": "ok"})


# @app.route('/image', methods=['POST'])
# def image_receive():
    
#     file = request.files['file']
#     if file:
#         filename = file.filename
#         file_path = os.path.join(UPLOAD_FOLDER, filename)
        
#         # Save the uploaded file
#         file.save(file_path)

#         # Move the most recent image to the RECENT_FOLDER
#         recent_file_path = os.path.join(RECENT_FOLDER, filename)
        
#         # Remove previous image in RECENT_FOLDER
#         for f in os.listdir(RECENT_FOLDER):
#             os.remove(os.path.join(RECENT_FOLDER, f))
        
#         # Copy the new image to RECENT_FOLDER
#         os.system(f'cp "{file_path}" "{recent_file_path}"')

#         # Maintain only the 3 most recent images in UPLOAD_FOLDER
#         maintain_recent_images()

#         return jsonify({"message": f"Image {filename} received and saved."}), 200
#     else:
#         return jsonify({"error": "No image received."}), 400

if __name__ == '__main__':
    # model_path = "/Users/cheongray/Y3S1/MDP/final_model_test/weights/best.pt"
    # model_path = "/Users/cheongray/Y3S1/MDP/final_model_test/weights/best_better.pt"
    model_path = "/Users/cheongray/Y3S1/MDP/final_model_test/weights/best_3.pt"
    img_folder = "/Users/cheongray/Y3S1/MDP/flask_test/object_upload_final"
    result_folder='results'
    json_folder='json_results'
    # class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'bulleye', 'circle', 'down', 'eight', 'five', 'four', 'left', 'nine', 'one', 'right', 'seven', 'six', 'three', 'two', 'up']
    class_names = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'bullseye', 'circle', 'down', 'left', 'right', 'up']
    model_handler = yolo_model(model_path, img_folder,result_folder=RESULT_FOLDER,json_folder= JSON_FOLDER,class_names=class_names)
    app.run(host='0.0.0.0', port=5055, debug=True)
