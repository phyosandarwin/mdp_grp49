import base64
from PIL import Image
from io import BytesIO

def decode_image(image_base64,result_image_filepath):
    if image_base64:
        # Decode the base64 string to bytes
        image_bytes = base64.b64decode(image_base64)
        # Convert bytes back into an image
        image = Image.open(BytesIO(image_bytes))
        image.save(result_image_filepath, 'JPEG') 
        print(f"Decoded image saved to {result_image_filepath}")
        return image
    else:
        raise ValueError("No image data found in the base64 string.")
