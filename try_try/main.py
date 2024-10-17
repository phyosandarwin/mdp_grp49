import cv2

def move_robot(direction, speed):
    # Placeholder function to send movement commands to the robot
    # direction: "left", "right", or "forward"
    # speed: how fast the robot should move
    print(f"Moving {direction} at speed {speed}")
    # Here, you would replace this with actual robot control code

def object_centering(camera_feed):
    while True:
        # Capture frame from camera
        ret, frame = camera_feed.read()

        # Convert to grayscale for processing (adjust according to your detection method)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Object detection (using a placeholder detection algorithm)
        object_cascade = cv2.CascadeClassifier('path/to/cascade.xml')
        objects = object_cascade.detectMultiScale(gray_frame, 1.1, 4)

        # Get frame dimensions
        frame_height, frame_width, _ = frame.shape
        frame_center_x = frame_width // 2

        for (x, y, w, h) in objects:
            # Draw a rectangle around the detected object
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Calculate object center
            object_center_x = x + w // 2

            # Calculate offset from frame center
            offset = object_center_x - frame_center_x

            # If object is not centered, adjust direction
            if abs(offset) > 20:  # Threshold to avoid jitter
                if offset > 0:
                    move_robot("right", speed=0.3)  # Adjust right
                else:
                    move_robot("left", speed=0.3)   # Adjust left
            else:
                # Object is centered, move forward
                move_robot("forward", speed=0.5)

        # Show frame for debugging
        cv2.imshow('Camera Feed', frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera_feed.release()
    cv2.destroyAllWindows()

# Initialize camera feed (change index if necessary)
camera_feed = cv2.VideoCapture(0)
object_centering(camera_feed)
