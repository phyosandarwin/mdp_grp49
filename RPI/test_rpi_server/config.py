import os
import time

class Config:
    # Folders
    IMAGE_FOLDER = 'images'
    RESULTS_FOLDER = 'image_results'



    # Limits and intervals
    MAX_IMAGES = 10
    CAPTURED_IMAGE_WAIT = 5  # in seconds

    # Server details
    MASTER_IP_ADDRESS = None 
    SERVER_PORT = 5055
    RETRY_DELAY = 2  
    RETRY_SEND_MAX = 5

    ALGO_PORT_NUMBER = 8001

    # # Bluetooth settings
    # STOP_IMAGE_REC = False


