from picamera import PiCamera
from time import sleep
import os
import base64
from PIL import Image
from io import BytesIO

class CameraHandler:
    def __init__(self,images_folder):
        # Initialize the PiCamera
        print('initiliasing camera')
        self.camera = PiCamera()
        # configure brightness contrast settings according to the current levels
        self.camera.contrast = 25
        self.camera.brightness = 75
        # self.camera.iso = 500
        self.camera.exposure_mode = 'backlight'
        self.image_storage  = images_folder
        if not os.path.exists( self.image_storage ):
            os.makedirs( self.image_storage )
    
    def maintain_recent_images(self):
        """Keeps only the  most recent images in the image storage folder."""
        images = sorted(os.listdir(self.image_storage), key=lambda x: os.path.getctime(os.path.join(self.image_storage, x)))
        if len(images) > self.MAX_IMAGES:
            for image in images[:-self.MAX_IMAGES]:
                print(f'remving image :{image}')
                os.remove(os.path.join(self.image_storage, image))
    
    def take_picture(self, filename):
        try:
            filepath = os.path.join(self.image_storage,filename)
            # Start the camera preview
            self.camera.start_preview()
            sleep(2)  # Let the camera warm up
            
            # Capture the image
            self.camera.capture(filepath)
            # print(f"Image saved as {filepath}")
            
            return filepath 
        finally:
            # Stop the camera preview
            self.camera.stop_preview()

    def close(self):
        # Close the camera
        self.camera.close()
