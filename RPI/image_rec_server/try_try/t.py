import time

def simulate_movement_to_center(bounding_box, frame_width, step_size=5):
    """
    Simulates movement to center an object in the frame based on bounding box coordinates.

    Parameters:
    bounding_box (list or tuple): The bounding box in the format (x_min, y_min, x_max, y_max)
    frame_width (int): The width of the frame or image.
    step_size (int): The amount of pixels to "move" in each iteration. Default is 5 pixels.

    Returns:
    None: Prints the steps taken to move the object to the center of the frame.
    """
    
    # Extract bounding box coordinates
    x_min, y_min, x_max, y_max = bounding_box

    # Calculate bounding box center
    center_x = (x_min + x_max) / 2

    # Frame center
    frame_center_x = frame_width / 2

    print(f"Initial bounding box center: {center_x:.2f}")
    print(f"Frame center: {frame_center_x:.2f}")

    # Simulate movement in steps to center the object
    while abs(center_x - frame_center_x) > step_size:
        offset = center_x - frame_center_x

        if offset > 0:
            # Object is to the right, move right
            print(f"Object is {offset:.2f} pixels to the right. Moving right by {step_size} pixels.")
            center_x -= step_size  # Simulate moving right
        elif offset < 0:
            # Object is to the left, move left
            print(f"Object is {abs(offset):.2f} pixels to the left. Moving left by {step_size} pixels.")
            center_x += step_size  # Simulate moving left

        time.sleep(0.5)  # Simulate time taken to move

    # When close enough to center, print success
    print(f"Object is centered at {center_x:.2f}. Moving forward.")

# Example usage
bounding_box = [932.1010, 265.2039, 1270.8949, 720.0000]
frame_width = 1920  # Assume the frame width is 1920 pixels

simulate_movement_to_center(bounding_box, frame_width)
