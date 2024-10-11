import pygame
import grid
import constants
import jsonParse
import obstacle
import math
import socket
import time
from path_finding import hamiltonian
from robot import robot
from robot.position import Position, RobotPosition
from robot.direction import Direction
from buttons import draw_button, handle_button_click, visitedSquares, draw_text_button
from run_algo import run_algo
import json


# Send the Commands to RPI
# RPI Connection
# Configure the client
server_ip = "10.96.49.1"  # Replace with your PC's IP address
server_port = 8007  # Use the same port number as on your PC

# # Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
print("Waiting to Connect to RPI")
client_socket.connect((server_ip, server_port))

print("Connected")

data = client_socket.recv(2048)

print(f"Received: {data.decode('utf-8')}")

obs = data.decode("utf-8")
print(f"Received: {data}")

pygame.init()
# Set up fonts
font = pygame.font.Font(None, 36)
running = True
screen = pygame.display.set_mode(
    (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.RESIZABLE
)
pygame.display.set_caption("Simulation")

# Create a Grid object
obstacles = [
    obstacle.Obstacle(screen, Position(50, 50, Direction.TOP), 1),
    obstacle.Obstacle(screen, Position(90, 90, Direction.BOTTOM), 2),
    obstacle.Obstacle(screen, Position(40, 180, Direction.BOTTOM), 3),
    obstacle.Obstacle(screen, Position(120, 150, Direction.RIGHT), 4),
    obstacle.Obstacle(screen, Position(150, 40, Direction.LEFT), 5),
    obstacle.Obstacle(screen, Position(190, 190, Direction.LEFT), 6),
]

# # Create a Grid object
# obstacles = [
#     obstacle.Obstacle(screen,Position(90,90, Direction.BOTTOM),1),
#     obstacle.Obstacle(screen,Position(90,90, Direction.RIGHT),2),
#     obstacle.Obstacle(screen,Position(90,90, Direction.TOP),3),
#     obstacle.Obstacle(screen,Position(90,90, Direction.LEFT),4)
# ]

# test1 = '{"cat":"obstacles","value":{"obstacles":[{"x":7,"y":14,"id":1,"d":0},{"x":15,"y":8,"id":2,"d":6},{"x":4,"y":3,"id":3,"d":2},{"x":9,"y":7,"id":4,"d":4}],"mode":"0"}}'

# test2 = '''{
#   "cat": "obstacles",
#   "value": {
#     "obstacles": [
#       {"x": 1, "y": 17, "id": 1, "d": 4},
#       {"x": 6, "y": 1, "id": 2, "d": 0},
#       {"x": 14, "y": 3, "id": 3, "d": 6},
#       {"x": 10, "y": 12, "id": 4, "d": 2},
#       {"x": 17, "y": 15, "id": 5, "d": 6},
#       {"x": 4, "y": 8, "id": 6, "d": 4},
#       {"x": 19, "y": 19, "id": 7, "d": 6},
#       {"x": 12, "y": 10, "id": 8, "d": 6}
#     ],
#     "mode": "0"
#   }
# }
# '''

# test3 = '''{
#   "cat": "obstacles",
#   "value": {
#     "obstacles": [
#       {"x": 5, "y": 9, "id": 1, "d": 4},
#       {"x": 7, "y": 14, "id": 2, "d": 6},
#       {"x": 12, "y": 9, "id": 3, "d": 2},
#       {"x": 15, "y": 15, "id": 4, "d": 4},
#       {"x": 15, "y": 4, "id": 5, "d": 6}
#     ],
#     "mode": "0"
#   }
# }
# '''


# result = jsonParse.parse_json(obs)
obstacles = jsonParse.convert_json(screen, obs)

# buttons
button_list = constants.BUTTON_LIST


grid = grid.Grid(screen, obstacles)
robot = robot.Robot(screen, grid, 0, 0)
print()
# hamiltonian = hamiltonian.Hamiltonian(robot,grid)
robot.setCurrentPos(0, 0, Direction.TOP)


# hamiltonian.get_path()
robot.setCurrentPos(
    constants.ROBOT_SAFETY_DISTANCE, constants.ROBOT_SAFETY_DISTANCE, Direction.TOP
)
hamiltonian = hamiltonian.Hamiltonian(robot, grid)
hamiltonian.get_path()


def get_commands(commands):
    output = []

    for command in commands:
        output.append(command.rpi_message())

    return ",".join(output)


commands_str = get_commands(hamiltonian.commands)

# "target": "AND"
rpi_commands = {
    "target": "STM",
    "cat": "path",
    "value": {"commands": commands_str},
}


# adding coords_str
def add_coords(command, dir):
    x, y = 0, 0
    if (command[:2]) == "SF":
        if dir == 0:
            y += int(command[2:])
        if dir == 1:
            x += int(command[2:])
        if dir == 2:
            y -= int(command[2:])
        if dir == 3:
            x -= int(command[2:])
    elif (command[:2]) == "SB":
        if dir == 0:
            y -= int(command[2:])
        if dir == 1:
            x -= int(command[2:])
        if dir == 2:
            y += int(command[2:])
        if dir == 3:
            x += int(command[2:])
    elif (command[:2]) == "LF":
        if dir == 0:
            x -= 30
            y += 20
        if dir == 1:
            x += 20
            y += 30
        if dir == 2:
            x += 30
            y -= 20
        if dir == 3:
            x -= 20
            y -= 30
        dir -= 1
        dir %= 4
    elif (command[:2]) == "RF":
        if dir == 0:
            x += 30
            y += 20
        if dir == 1:
            x += 20
            y -= 30
        if dir == 2:
            x -= 30
            y -= 20
        if dir == 3:
            x -= 20
            y += 30
        dir += 1
        dir %= 4
    elif (command[:2]) == "LB":
        if dir == 0:
            x -= 20
            y -= 30
        if dir == 1:
            x -= 30
            y += 20
        if dir == 2:
            x += 20
            y += 30
        if dir == 3:
            x += 30
            y -= 20
        dir += 1
        dir %= 4
    elif (command[:2]) == "RB":
        if dir == 0:
            x += 20
            y -= 30
        if dir == 1:
            x -= 30
            y -= 20
        if dir == 2:
            x -= 20
            y += 30
        if dir == 3:
            x += 30
            y += 20
        dir -= 1
        dir %= 4
    return (x, y, dir)


coords = []
x, y, dir = 0, 0, 0
for command in commands_str.split(","):
    _x, _y, dir = add_coords(command, dir)
    x += _x
    y += _y
    x_ = x
    y_ = y
    dir_ = ""
    if dir == 0:
        y_ += 20
        dir_ = "N"
    elif dir == 1:
        x_ += 20
        y_ += 20
        dir_ = "E"
    elif dir == 2:
        x_ += 20
        dir_ = "S"
    elif dir == 3:
        dir_ = "W"
    coords.append((x_, y_, dir_))

print(coords)

rpi_commands["value"]["coords"] = coords
rpi_commands_json = json.dumps(rpi_commands)

print(rpi_commands)

client_socket.send(rpi_commands_json.encode("utf-8"))

robot.setCurrentPos(0, 0, Direction.TOP)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos
                handle_button_click(event.pos, robot, button_list)
                if (
                    constants.START_BUTTON["x"]
                    <= mouse_x
                    <= constants.START_BUTTON["x"] + constants.START_BUTTON["width"]
                    and constants.START_BUTTON["y"]
                    <= mouse_y
                    <= constants.START_BUTTON["y"] + constants.START_BUTTON["height"]
                ):
                    run_algo(robot, grid)

    screen.fill((224, 235, 235))
    for button in button_list:
        draw_button(
            screen,
            button["path"],
            button["x"],
            button["y"],
            button["width"],
            button["height"],
            (169, 169, 169),
            (128, 128, 128),
        )
    draw_text_button(screen, constants.START_BUTTON)

    # if count == 0:

    # robot.draw_robot()
    # count = run_algo(robot, hamiltonian.commands, grid, count)

    grid.draw_grid(visitedSquares)
    robot.draw_robot()
    pygame.display.update()
