import glob
import os
images_path = '/home/pi/test_rpi_server_2/mdp_grp49/RPI/test_rpi_server/images'
files = glob.glob(os.path.join(images_path,'*'))

for file in files:
    try:
        os.remove(file)
        print(f"Deleted{file}")
    except Exception as e:
        print(e)