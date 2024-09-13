import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from model import yolo_model
from image_handler import get_encoded_image
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
RECENT_FOLDER = 'recent'

RESULT_FOLDER='results'
JSON_FOLDER='json_results'
model_handler = None

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RECENT_FOLDER, exist_ok=True)

def remove_file(folder, filename):
    file_path = os.path.join(folder, filename)
    
    # Check if the file exists
    if os.path.exists(file_path):
        os.remove(file_path)  # Remove the file
        print(f"File {filename} has been removed.")
    else:
        print(f"File {filename} not found in {folder}.")




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
    global model_handler
    
    if file:
        filename = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        

        file.save(file_path)

        recent_file_path = os.path.join(RECENT_FOLDER, filename)
        
    
        for f in os.listdir(RECENT_FOLDER):
            os.remove(os.path.join(RECENT_FOLDER, f))
        
        os.system(f'cp "{file_path}" "{recent_file_path}"')

        maintain_recent_images(UPLOAD_FOLDER, 3)
        result,bounding_box_flag = model_handler.run_inference(filename)
        if bounding_box_flag:#means got save into results folder
            result_image_filepath = os.path.join(RESULT_FOLDER,filename)
            encoded_image= get_encoded_image(result_image_filepath)

            result['encoded_image'] = encoded_image
            maintain_recent_images(RESULT_FOLDER, 3)
            return jsonify(result), 200
        else:
            return jsonify(result), 200
        
        
    else:
        return jsonify({"error": "No image received."}), 400





@app.route('/status', methods=['GET'])
def status():
    return jsonify({"result": "ok"})

@app.route('/image', methods=['POST'])
def image_receive():
    file = request.files['file']
    if file:
        filename = file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save the uploaded file
        file.save(file_path)

        # Move the most recent image to the RECENT_FOLDER
        recent_file_path = os.path.join(RECENT_FOLDER, filename)
        
        # Remove previous image in RECENT_FOLDER
        for f in os.listdir(RECENT_FOLDER):
            os.remove(os.path.join(RECENT_FOLDER, f))
        
        # Copy the new image to RECENT_FOLDER
        os.system(f'cp "{file_path}" "{recent_file_path}"')

        # Maintain only the 3 most recent images in UPLOAD_FOLDER
        maintain_recent_images()

        return jsonify({"message": f"Image {filename} received and saved."}), 200
    else:
        return jsonify({"error": "No image received."}), 400

if __name__ == '__main__':
    model_path = "/Users/cheongray/Y3S1/MDP/final_model_test/weights/best.pt"
    img_folder = "/Users/cheongray/Y3S1/MDP/flask_test/recent"
    result_folder='results'
    json_folder='json_results'
    class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'bulleye', 'circle', 'down', 'eight', 'five', 'four', 'left', 'nine', 'one', 'right', 'seven', 'six', 'three', 'two', 'up']
    model_handler = yolo_model(model_path, img_folder,result_folder=RESULT_FOLDER,json_folder= JSON_FOLDER,class_names=class_names)
    app.run(host='0.0.0.0', port=5055, debug=True)
