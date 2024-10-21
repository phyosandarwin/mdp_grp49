# import os
# import time
# import json
# from ultralytics import YOLO
# from image_handler import get_image_from_folder
# import torch

# class yolo_model:
#     def __init__(self, model_path, img_folder, result_folder,json_folder,class_names):
#         self.model_path = model_path
#         self.img_folder = img_folder
#         self.result_folder = result_folder
#         self.json_folder = json_folder
#         self.class_names = class_names
        
#         # Load the model
#         start_time = time.time()
#         self.model = YOLO(self.model_path)
#         end_time = time.time()
#         duration = end_time - start_time
#         print(f"Time taken to load the model: {duration:.4f} seconds")
        
#         # Create results folder if it doesn't exist
#         if not os.path.exists(self.result_folder):
#             os.makedirs(self.result_folder)
#         if not os.path.exists(self.json_folder):
#             os.makedirs(self.json_folder)
        
        
#     def run_inference(self,name_of_file, folder_name):
#         # Get the image from the specified folder
#         print("GETTING IMAGE FROM ",os.path.join(self.img_folder, folder_name,name_of_file))
#         img_path = os.path.join(self.img_folder,folder_name,name_of_file)
#         # Run inference (prediction) on the image
#         results = self.model(img_path)
#         # print("---df results:---")
#         # print(results.pandas().xyxy[0])

#         # print(results)
#         for i, result in enumerate(results):
#             print(f"Result {i + 1}:")
            
#             if result.boxes:
#                 boxes = result.boxes.xyxy  # Coordinates for the bounding boxes
#                 conf = result.boxes.conf  # Confidence scores for the boxes
#                 class_indices = result.boxes.cls
                
#                 labels = [self.class_names[int(cls)] for cls in class_indices] 
#                 print("Bounding Boxes:")
#                 print(boxes)
#                 print("Confidence Scores:")
#                 print(conf)
#                 max_value, max_index = torch.max(conf, dim=0)
#                 print(f"max confidence score {max_value} for class label:{conf[max_index]} ")
#                 print("Labels:")
#                 print(labels)
                
#                 result_dict = {
#                     "boxes": boxes.tolist(),
#                     "confidence": conf.tolist(),
#                     'class_name' : labels
#                 }
#                 result_json = json.dumps(result_dict, indent=4)
#                 json_path = os.path.join(self.json_folder, 'result.json')
#                 with open(json_path, 'w') as json_file:
#                     json_file.write(result_json)

#                 save_path = os.path.join(self.result_folder,folder_name, f'{name_of_file}')
#                 print(f"Saving result to: {save_path}")
#                 result.save(filename=save_path)
#                 return result_dict,True#return dict so can still add image ot dict then conevrt to json
#             else:
#                 result_dict = {
#                     "boxes": None,
#                     "confidence": None
#                 }
#                 result_json = json.dumps(result_dict, indent=4)
#                 json_path = os.path.join(self.json_folder, 'result.json')
#                 with open(json_path, 'w') as json_file:
#                     json_file.write(result_json)
#                 print("No bounding boxes found.")
#                 return result_dict,False#return dict so can still add image ot dict then conevrt to json
            
#             # Save the result image with bounding boxes

import os 
import cv2 
import time 
from ultralytics import YOLO  
import json
class yolo_model: 
    def __init__(self, model_path, img_folder, result_folder,json_folder,name_id_dict): 
        self.model_path = model_path 
        self.img_folder = img_folder 
        self.result_folder = result_folder 
        self.json_folder = json_folder 
        self.name_to_id = name_id_dict 
         
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
     
    def draw_own_bbox(self, img, x1, y1, x2, y2, label, color=(36, 255, 12), text_color=(0, 0, 0)): 
        """ 
        Draw bounding box on the image with text label and save both the raw and annotated image in the 'own_results' folder 
        """ 
        # Convert the coordinates to int 
        x1 = int(x1) 
        x2 = int(x2) 
        y1 = int(y1) 
        y2 = int(y2) 
 
        # Draw the bounding box 
        img = cv2.rectangle(img, (x1, y1), (x2, y2), color, 2) 
         
        # For the text background, find space required by the text 
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1) 
        # Print the text   
        img = cv2.rectangle(img, (x1, y1 - 20), (x1 + w, y1), color, -1) 
        img = cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 1) 
         
        return img     
         
    def run_inference(self, name_of_file, folder_name): 
        # Get the image from the specified folder 
        print("GETTING IMAGE FROM ", os.path.join(self.img_folder, folder_name, name_of_file)) 
        img_path = os.path.join(self.img_folder, folder_name, name_of_file) 
         
        # Load the image using OpenCV for drawing bounding boxes later 
        img = cv2.imread(img_path) 
 
        # Run inference (prediction) on the image 
        results = self.model(img_path) 
        print('===Results===') 
         
        for i, result in enumerate(results): 
            print(f"Result {i + 1}:") 
             
            if result.boxes: 
                boxes = result.boxes.xyxy  # Coordinates for the bounding boxes 
                conf = result.boxes.conf  # Confidence scores for the boxes 
                class_indices = result.boxes.cls 
                 
                # Map class indices to class names using name_to_id keys 
                labels = [list(self.name_to_id.keys())[int(cls)] for cls in class_indices]
                # labels = [label if label != "bullseye" else "" for label in labels]
                # labels = [label in labels if label != "bullseye" else ""]
                # print(labels)
                # labels.remove('bullseye')
                print(labels)
                # Map labels to corresponding ids using name_to_id dictionary 
                ids = [self.name_to_id.get(label, -1) for label in labels] 

                print("Bounding Boxes (xyxy):") 
                print(boxes)        
                print(f"Confidence Scores: {conf}") 
                print(f"Labels: {labels}") 
                print(f"Class ids: {ids}")
 
                # Draw bounding boxes using the draw_own_bbox function 
                for j, (box, label, score) in enumerate(zip(boxes, labels, conf)): 
                    x1, y1, x2, y2 = box  # Unpack the coordinates of the bounding box 
                    class_id = self.name_to_id[label] 
                     
                    # Format the label to include class, ID, and confidence score 
                    display_text = f"{class_id} ({score:.2f})" 
                     
                    # Pass the formatted display text with the confidence score to the draw_own_bbox function 
                    self.draw_own_bbox(img, x1, y1, x2, y2, display_text) 
 
                # Save the annotated image after drawing bounding boxes 
                save_path = os.path.join(self.result_folder, folder_name, f'{name_of_file}') 
                cv2.imwrite(save_path, img) 
                print(f"Saving annotated image to: {save_path}") 
 
                # Save result in JSON format
                result_dict = { 
                    "boxes": boxes.tolist(), 
                    "confidence": conf.tolist(), 
                    'class_ids': ids 
                } 
                result_json = json.dumps(result_dict, indent=4) 
                json_path = os.path.join(self.json_folder, 'result.json') 
                with open(json_path, 'w') as json_file: 
                    json_file.write(result_json) 
                print(f"Saving result JSON to: {json_path}") 
                 
                return result_dict, True 
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
                return result_dict, False
