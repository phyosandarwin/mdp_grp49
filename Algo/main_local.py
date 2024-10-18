import pygame
import grid
import constants
import jsonParse
import obstacle
import socket
from path_finding import hamiltonian
from robot import robot
from robot.position import Position
from robot.direction import Direction
from buttons import draw_button, handle_button_click, visitedSquares, draw_text_button
from run_algo import run_algo
import json

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
    obstacle.Obstacle(screen, Position(20, 150, Direction.BOTTOM), 1),
    obstacle.Obstacle(screen, Position(80, 110, Direction.LEFT), 2),
    obstacle.Obstacle(screen, Position(70, 10, Direction.TOP), 3),
    obstacle.Obstacle(screen, Position(150, 30, Direction.LEFT), 4),
]

obstacles = [
    obstacle.Obstacle(screen, Position(10, 180, Direction.BOTTOM), 1),
    obstacle.Obstacle(screen, Position(60, 120, Direction.TOP), 2),
    obstacle.Obstacle(screen, Position(100, 70, Direction.LEFT), 3),
    obstacle.Obstacle(screen, Position(130, 20, Direction.RIGHT), 4),
    obstacle.Obstacle(screen, Position(150, 160, Direction.BOTTOM), 5),
    obstacle.Obstacle(screen, Position(190, 90, Direction.LEFT), 6),
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
    fr1, fr2 = 30, 20
    fl1, fl2 = 30, 20
    br1, br2 = 30, 30
    bl1, bl2 = 20, 30
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
            x -= fl1
            y += fl2
        if dir == 1:
            x += fl2
            y += fl1
        if dir == 2:
            x += fl1
            y -= fl2
        if dir == 3:
            x -= fl2
            y -= fl1
        dir -= 1
        dir %= 4
    elif (command[:2]) == "RF":
        if dir == 0:
            x += fr1
            y += fr2
        if dir == 1:
            x += fr2
            y -= fr1
        if dir == 2:
            x -= fr1
            y -= fr2
        if dir == 3:
            x -= fr2
            y += fr1
        dir += 1
        dir %= 4
    elif (command[:2]) == "LB":
        if dir == 0:
            x -= bl1
            y -= bl2
        if dir == 1:
            x -= bl2
            y += bl1
        if dir == 2:
            x += bl1
            y += bl2
        if dir == 3:
            x += bl2
            y -= bl1
        dir += 1
        dir %= 4
    elif (command[:2]) == "RB":
        if dir == 0:
            x += br1
            y -= br2
        if dir == 1:
            x -= br2
            y -= br1
        if dir == 2:
            x -= br1
            y += br2
        if dir == 3:
            x += br2
            y += br1
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
