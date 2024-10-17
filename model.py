import os
import time
import json
from ultralytics import YOLO
from image_handler import get_image_from_folder
import torch

class yolo_model:
    def __init__(self, model_path, img_folder, result_folder,json_folder,class_names):
        self.model_path = model_path
        self.img_folder = img_folder
        self.result_folder = result_folder
        self.json_folder = json_folder
        self.class_names = class_names
        
        # Load the model
        start_time = time.time()
        self.model = YOLO(self.model_path)
        end_time = time.time()
        duration = end_time - start_time
        print(f"Time taken to load the model: {duration:.4f} seconds")
        
        # Create results folder if it doesn't exist
        if not os.path.exists(self.result_folder):
            os.makedirs(self.result_folder)
        if not os.path.exists(self.json_folder):
            os.makedirs(self.json_folder)
        
        
    def run_inference(self,name_of_file, folder_name):
        # Get the image from the specified folder
        print("GETTING IMAGE FROM ",os.path.join(self.img_folder, folder_name,name_of_file))
        img_path = os.path.join(self.img_folder,folder_name,name_of_file)
        # Run inference (prediction) on the image
        results = self.model(img_path)
        print('===results===')
        # print(results)
        for i, result in enumerate(results):
            print(f"Result {i + 1}:")
            
            if result.boxes:
                boxes = result.boxes.xyxy  # Coordinates for the bounding boxes
                conf = result.boxes.conf  # Confidence scores for the boxes
                class_indices = result.boxes.cls
                
                labels = [self.class_names[int(cls)] for cls in class_indices] 
                print("Bounding Boxes:")
                print(boxes)
                print("Confidence Scores:")
                print(conf)
                max_value, max_index = torch.max(conf, dim=0)
                print(f"max confidence score {max_value} for class label:{conf[max_index]} ")
                print("Labels:")
                print(labels)
                
                result_dict = {
                    "boxes": boxes.tolist(),
                    "confidence": conf.tolist(),
                    'class_name' : labels
                }
                result_json = json.dumps(result_dict, indent=4)
                json_path = os.path.join(self.json_folder, 'result.json')
                with open(json_path, 'w') as json_file:
                    json_file.write(result_json)

                save_path = os.path.join(self.result_folder,folder_name, f'{name_of_file}')
                print(f"Saving result to: {save_path}")
                result.save(filename=save_path)
                return result_dict,True#return dict so can still add image ot dict then conevrt to json
            else:
                result_dict = {
                    "boxes": None,
                    "confidence": None
                }
                result_json = json.dumps(result_dict, indent=4)
                json_path = os.path.join(self.json_folder, 'result.json')
                with open(json_path, 'w') as json_file:
                    json_file.write(result_json)
                print("No bounding boxes found.")
                return result_dict,False#return dict so can still add image ot dict then conevrt to json
            
            # Save the result image with bounding boxes


# # Usage example
# if __name__ == '__main__':
#     model_path = "/Users/cheongray/Y3S1/MDP/final_model_test/weights/best.pt"
#     img_folder = "/Users/cheongray/Downloads/"
#     model_handler = YOLOModelHandler(model_path, img_folder)
#     model_handler.run_inference()
#/Users/cheongray/Y3S1/MDP/flask_test/results/captured_image_20240908-053841.jpg.jpg