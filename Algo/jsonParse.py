import json
import pygame
import obstacle
import constants
from robot.position import Position, RobotPosition
from robot.direction import Direction


# parse JSON file
def parse_json(json_str):
    try:
        data = json.loads(json_str)
        if "cat" in data and "value" in data:
            cat = data["cat"]
            value = data["value"]
            if "obstacles" in value and "mode" in value:
                obstacles = value["obstacles"]
                mode = value["mode"]
                return cat, obstacles, mode
    except json.JSONDecodeError:
        pass

    # If the JSON data doesn't match the expected structure, return None
    return None


# convert JSON file to obstacles object using specified format
import ast


def convert_json(screen, obstacle_list_str):
    # Convert the string representation of the list to an actual list
    try:
        obstacle_list = ast.literal_eval(obstacle_list_str)
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Error converting string to list: {str(e)}")

    new_obstacles = []

    for obstacle_str in obstacle_list:
        # Strip any unwanted characters and extra spaces
        obstacle_str = obstacle_str.strip()

        # Split the string by commas to get x, y, direction, and id
        parts = obstacle_str.split(",")

        # Ensure that we have exactly 4 parts (x, y, direction, id)
        if len(parts) != 4:
            raise ValueError(f"Invalid obstacle format: {obstacle_str}")

        try:
            # Parse the x, y coordinates and id
            new_x = int(parts[0].strip()) * 10
            new_y = int(parts[1].strip()) * 10
            obstacle_id = parts[3].strip()

            # Map the direction character to the corresponding Direction enum
            direction_char = parts[2].strip()
            if direction_char == "N":
                new_d = Direction.TOP
            elif direction_char == "E":
                new_d = Direction.RIGHT
            elif direction_char == "S":
                new_d = Direction.BOTTOM
            elif direction_char == "W":
                new_d = Direction.LEFT
            else:
                raise ValueError(f"Unknown direction: {direction_char}")

            # Create a new Obstacle object and add it to the list
            new_obstacles.append(
                obstacle.Obstacle(screen, Position(new_x, new_y, new_d), obstacle_id)
            )

        except ValueError as e:
            raise ValueError(f"Error parsing obstacle: {obstacle_str} - {str(e)}")

    return new_obstacles


# Example usage:
# json_str = '{"cat":"obstacles","value":{"obstacles":[{"x":7,"y":14,"id":1,"d":0},{"x":15,"y":8,"id":2,"d":6},{"x":4,"y":3,"id":3,"d":2},{"x":9,"y":7,"id":4,"d":4}],"mode":"0"}}'
# result = parse_json(json_str)
# screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.RESIZABLE)
# print(convert_json(screen, result))

# if result:
#     cat, obstacles, mode = result
#     print(f'Category: {cat}')
#     print(f'Obstacles: {obstacles}')
#     print(f'Mode: {mode}')
# else:
#     print('Invalid JSON structure')
