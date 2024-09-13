import os
from PIL import Image
from base64 import encodebytes
import io
def get_image_from_folder(folder_path):
    # Get list of all files in the folder
    files = os.listdir(folder_path)

    # Filter out image files based on extensions (e.g., .jpg, .png)
    image_extensions = ['.jpg', '.jpeg', '.png']
    image_files = [f for f in files if os.path.splitext(f)[1].lower() in image_extensions]

    if not image_files:
        print("No images found in the folder.")
        return None
    #return the first image found
    image_path = os.path.join(folder_path, image_files[0])
    print(f"Image found: {image_path}")
    return image_path
def get_encoded_image(image_path):
    pil_img = Image.open(image_path, mode='r')  # Open the image file
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='JPEG')  # Convert the image to byte array (JPEG)
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')  # Encode as base64
    return encoded_img