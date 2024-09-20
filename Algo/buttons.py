import pygame
from robot import robot
import constants
from robot.turn_type import TurnType
from robot.direction import Direction

def draw_text_button(surface, button, text_color=(255, 255, 255)):
    mouse = pygame.mouse.get_pos()
    
    x, y, width, height = button['x'], button['y'], button['width'], button['height']
    
    # Font
    font = pygame.font.Font(None, 36)
    
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(surface, (0, 0, 255), (x, y, width, height))
    else:
        pygame.draw.rect(surface, (0, 128, 255), (x, y, width, height))
    
    text_surface = font.render(button['text'], True, text_color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x + width // 2, y + height // 2)
    
    surface.blit(text_surface, text_rect)

def draw_button(surface, image_path, x, y, width, height, original_color, hover_color):
    mouse = pygame.mouse.get_pos()

    button_image = pygame.image.load(image_path)
    button_image = pygame.transform.scale(button_image, (width, height))

    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(surface, hover_color, (x, y, width, height))
        surface.blit(button_image, (x, y))
        return True  
    else:
        pygame.draw.rect(surface, original_color, (x, y, width, height))
        surface.blit(button_image, (x, y))
        return False  

def get_covered_turn_squares(curr_pos, reverse, step_size=10):
    squares = []
    orientation = curr_pos.direction
    if not reverse:
        if orientation == Direction.TOP:
            squares = [(curr_pos.x + i*step_size, curr_pos.y  + j*step_size) for i in range(3) for j in range(5)]
        elif orientation == Direction.RIGHT:
            squares = [(curr_pos.x + i*step_size, curr_pos.y  + j*step_size) for i in range(5) for j in range(3)]
        elif orientation == Direction.BOTTOM:
            squares = [(curr_pos.x + i*step_size, curr_pos.y  - j*step_size) for i in range(3) for j in range(3)]
        elif orientation == Direction.LEFT:
            squares = [(curr_pos.x - i*step_size, curr_pos.y  + j*step_size) for i in range(3) for j in range(3)]
    if reverse:
        if orientation == Direction.BOTTOM:
            squares = [(curr_pos.x + i*step_size, curr_pos.y  + j*step_size) for i in range(3) for j in range(6)]
        elif orientation == Direction.LEFT:
            squares = [(curr_pos.x + i*step_size, curr_pos.y  + j*step_size) for i in range(6) for j in range(3)]
        elif orientation == Direction.TOP:
            squares = [(curr_pos.x + i*step_size, curr_pos.y  - j*step_size) for i in range(3) for j in range(4)]
        elif orientation == Direction.RIGHT:
            squares = [(curr_pos.x - i*step_size, curr_pos.y  + j*step_size) for i in range(4) for j in range(3)]
    return squares
    
def get_covered_slant_squares(curr_pos, reverse, step_size=10):
    squares = []
    orientation = curr_pos.direction
    if not reverse:
        if orientation == Direction.TOP:
            squares = [(curr_pos.x + i*step_size, curr_pos.y + j*step_size) for i in range(3) for j in range(4)]
        elif orientation == Direction.RIGHT:
            squares = [(curr_pos.x + i*step_size, curr_pos.y + j*step_size) for i in range(4) for j in range(3)]
        elif orientation == Direction.BOTTOM:
            squares = [(curr_pos.x + i*step_size, curr_pos.y - j*step_size) for i in range(3) for j in range(2)]
        elif orientation == Direction.LEFT:
            squares = [(curr_pos.x - i*step_size, curr_pos.y + j*step_size) for i in range(2) for j in range(3)]
    if reverse:
        if orientation == Direction.BOTTOM:
            squares = [(curr_pos.x + i*step_size, curr_pos.y + j*step_size) for i in range(3) for j in range(4)]
        elif orientation == Direction.LEFT:
            squares = [(curr_pos.x + i*step_size, curr_pos.y + j*step_size) for i in range(4) for j in range(3)]
        elif orientation == Direction.TOP:
            squares = [(curr_pos.x + i*step_size, curr_pos.y - j*step_size) for i in range(3) for j in range(2)]
        elif orientation == Direction.RIGHT:
            squares = [(curr_pos.x - i*step_size, curr_pos.y + j*step_size) for i in range(2) for j in range(3)]
    return squares

visitedSquares = constants.INIT_VISITED
def handle_button_click( pos, robot, button_list):
    global visitedSquares
    x, y = pos
    turnSquares = []
    squares = []
    slant_squares = []
    init = robot.get_current_pos()
    step_size = 10
    # print(init.x,init.y)
    for i, button in enumerate(button_list):
        if button['x'] <= x <= button['x'] + button['width'] and button['y'] <= y <= button['y'] + button['height']:
            if button['path'] == './images/Forward.png':
                robot.straight(10)
                # print(robot.get_current_pos())
                # print(visitedSquares)
            elif button['path'] == './images/Reverse.png':
                robot.straight(-10)
                print(robot.get_current_pos())
            elif button['path'] == './images/JockeyForwardLeft.png':
                slant_squares = get_covered_slant_squares(robot.get_current_pos(), False)
                robot.turn(TurnType.SMALL, True, False,
                        False)
                print(robot.get_current_pos())
            elif button['path'] == './images/JockeyForwardRight.png':
                slant_squares = get_covered_slant_squares(robot.get_current_pos(), False)
                robot.turn(TurnType.SMALL, False, True,
                        False)
                # print(robot.get_current_pos())
            elif button['path'] == './images/ForwardLeft.png':
                turnSquares = get_covered_turn_squares(robot.get_current_pos(), False)
                robot.turn(TurnType.MEDIUM, True, False,
                        False)
                # print(robot.get_current_pos())
            elif button['path'] == './images/ForwardRight.png':
                turnSquares = get_covered_turn_squares(robot.get_current_pos(), False)
                robot.turn(TurnType.MEDIUM, False, True,
                        False)
                # print(robot.get_current_pos())
            elif button['path'] == './images/ReverseLeft.png':
                turnSquares = get_covered_turn_squares(robot.get_current_pos(), True)
                robot.turn(TurnType.MEDIUM, True, False,
                        True)
                # print(robot.get_current_pos())
            elif button['path'] == './images/ReverseRight.png':
                turnSquares = get_covered_turn_squares(robot.get_current_pos(), True)
                robot.turn(TurnType.MEDIUM, False, True,
                        True)
                # print(robot.get_current_pos())
            elif button['path'] == './images/JockeyReverseLeft.png':
                slant_squares = get_covered_slant_squares(robot.get_current_pos(), True)
                robot.turn(TurnType.SMALL, True, False,
                        True)
                # print(robot.get_current_pos())
            elif button['path'] == './images/JockeyReverseRight.png':
                slant_squares = get_covered_slant_squares(robot.get_current_pos(), True)
                robot.turn(TurnType.SMALL, False, True,
                        True)
                # print(robot.get_current_pos())
            
            # print(slant_squares)
            squares = [(init.x + i*step_size, init.y + j*step_size) for i in range(3) for j in range(3)]
            visitedSquares += squares
            visitedSquares += turnSquares
            visitedSquares += slant_squares
            break  




