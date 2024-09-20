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
        if 'cat' in data and 'value' in data:
            cat = data['cat']
            value = data['value']
            if 'obstacles' in value and 'mode' in value:
                obstacles = value['obstacles']
                mode = value['mode']
                return cat, obstacles, mode
    except json.JSONDecodeError:
        pass

    # If the JSON data doesn't match the expected structure, return None
    return None

# convert JSON file to obstacles object using specified format
def convert_json(screen, json):
    new_obstacles = []
    cat, obstacles, mode = json
    for dict in obstacles:

        new_x = dict['x']*10
        new_y = dict['y']*10
        if dict['d'] == 0:
            new_d = Direction.TOP
        elif dict['d'] == 2:
            new_d = Direction.RIGHT
        elif dict['d'] == 4:
            new_d = Direction.BOTTOM
        elif dict['d'] == 6:
            new_d = Direction.LEFT
        
        new_obstacles.append(
            obstacle.Obstacle(screen,Position(new_x,new_y, new_d),dict['id']))
    
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