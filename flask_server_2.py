import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from model import yolo_model
from image_handler import get_encoded_image
from algo import Algo

class FlaskServer:
    def __init__(self, model_path, img_folder, result_folder, json_folder, class_names):
        self.app = Flask(__name__)
        CORS(self.app)
        self.model_handler = yolo_model(model_path, img_folder, result_folder, json_folder, class_names)

        # image handling
        self.UPLOAD_FOLDER = 'uploads'
        self.RECENT_FOLDER = 'recent'
        self.RESULT_FOLDER = result_folder
        self.JSON_FOLDER = json_folder
        
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.RECENT_FOLDER, exist_ok=True)

        # Routes
        self.app.add_url_rule('/predict', 'predict', self.predict, methods=['POST'])
        self.app.add_url_rule('/algo', 'algo_receive', self.algo_receive, methods=['POST'])
        self.app.add_url_rule('/status', 'status', self.status, methods=['GET'])
        self.app.add_url_rule('/image', 'image_receive', self.image_receive, methods=['POST'])

    def remove_file(self, folder, filename):
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File {filename} has been removed.")
        else:
            print(f"File {filename} not found in {folder}.")

    def maintain_recent_images(self, folder, max_images=3):
        images = sorted(os.listdir(folder), key=lambda x: os.path.getctime(os.path.join(folder, x)))
        if len(images) > max_images:
            for image in images[:-max_images]:
                os.remove(os.path.join(folder, image))
                print(f"Removed {image} from {folder}")

    def predict(self):
        file = request.files['file']
        if file:
            filename = file.filename
            file_path = os.path.join(self.UPLOAD_FOLDER, filename)
            file.save(file_path)

            recent_file_path = os.path.join(self.RECENT_FOLDER, filename)
            for f in os.listdir(self.RECENT_FOLDER):
                os.remove(os.path.join(self.RECENT_FOLDER, f))
            os.system(f'cp "{file_path}" "{recent_file_path}"')

            self.maintain_recent_images(self.UPLOAD_FOLDER)

            result, bounding_box_flag = self.model_handler.run_inference(filename)
            if bounding_box_flag:
                result_image_filepath = os.path.join(self.RESULT_FOLDER, filename)
                self.maintain_recent_images(self.RESULT_FOLDER)
                return jsonify(result), 200
            else:
                return jsonify(result), 200
        else:
            return jsonify({"error": "No image received."}), 400

    def algo_receive(self):
        get_algo_commands = Algo()
        data_from_android = request.get_json()
        if data_from_android and 'data' in data_from_android:
            received_array = data_from_android['data']
            number_of_obs = len(received_array)

            main_dir = 'obs_results'
            os.makedirs(main_dir, exist_ok=True)

            for i in range(1, number_of_obs + 1):
                subfolder = os.path.join(main_dir, f'obs_{i}')
                os.makedirs(subfolder, exist_ok=True)

            received_android_info = {"status": "success", "received_data": received_array}
            robot_commands = get_algo_commands.return_algo()
            combined_json = {**received_android_info, **robot_commands}

            return jsonify(combined_json), 200
        else:
            return jsonify({"error": "Invalid data received."}), 400

    def status(self):
        return jsonify({"result": "ok"})

    def image_receive(self):
        file = request.files['file']
        if file:
            filename = file.filename
            file_path = os.path.join(self.UPLOAD_FOLDER, filename)
            file.save(file_path)

            recent_file_path = os.path.join(self.RECENT_FOLDER, filename)
            for f in os.listdir(self.RECENT_FOLDER):
                os.remove(os.path.join(self.RECENT_FOLDER, f))
            os.system(f'cp "{file_path}" "{recent_file_path}"')

            self.maintain_recent_images(self.UPLOAD_FOLDER)

            return jsonify({"message": f"Image {filename} received and saved."}), 200
        else:
            return jsonify({"error": "No image received."}), 400

    def run(self):
        self.app.run(host='0.0.0.0', port=5055, debug=True)


if __name__ == '__main__':
    model_path = "/Users/cheongray/Y3S1/MDP/final_model_test/weights/best_better.pt"
    img_folder = "/Users/cheongray/Y3S1/MDP/flask_test/recent"
    result_folder = 'results'
    json_folder = 'json_results'
    class_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'bulleye', 'circle', 'down', 'eight', 'five', 'four', 'left', 'nine', 'one', 'right', 'seven', 'six', 'three', 'two', 'up']
    
    flask_server = FlaskServer(model_path, img_folder, result_folder, json_folder, class_names)
    flask_server.run()
