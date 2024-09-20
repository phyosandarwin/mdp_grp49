import time
from commands.turn_command import TurnCommand
from commands.straight_command import StraightCommand
from commands.scan_command import ScanCommand
from robot.robot import Robot
import pygame
from grid import Grid
import constants
from buttons import get_covered_slant_squares, get_covered_turn_squares
from robot.turn_type import TurnType
from path_finding.hamiltonian import Hamiltonian
from robot.direction import Direction

def get_command_for_movement(command):
    if isinstance(command, StraightCommand):
        if command.dist > 0:
            return './images/Forward.png'
        elif command.dist < 0:
            return './images/Reverse.png'
    elif isinstance(command, TurnCommand):
        turn_type = command.type_of_turn
        left = command.left
        right = command.right
        reverse = command.reverse
        
        if turn_type == TurnType.SMALL:
            if left and not right and not reverse:
                return './images/JockeyForwardLeft.png'
            elif not left and right and not reverse:
                return './images/JockeyForwardRight.png'
            elif left and not right and reverse:
                return './images/JockeyReverseLeft.png'
            elif not left and right and reverse:
                return './images/JockeyReverseRight.png'
        elif turn_type == TurnType.MEDIUM:
            if left and not right and not reverse:
                return './images/ForwardLeft.png'
            elif not left and right and not reverse:
                return './images/ForwardRight.png'
            elif left and not right and reverse:
                return './images/ReverseLeft.png'
            elif not left and right and reverse:
                return './images/ReverseRight.png'
    
    # If no matching command is found, return None
    return None



def run_algo(robot,  grid, step_size = 10):
    robot.setCurrentPos(constants.ROBOT_SAFETY_DISTANCE, constants.ROBOT_SAFETY_DISTANCE, Direction.TOP)
    hamiltonian = Hamiltonian(robot,grid)
    hamiltonian.get_path()
    commands = hamiltonian.commands
    clock = pygame.time.Clock()
    visitedSquares = constants.INIT_VISITED
    robot.setCurrentPos(0, 0, Direction.TOP)


    robot.draw_robot() 
    for command in commands:
        
        if isinstance(command, TurnCommand):
            init = robot.get_current_pos()
            clock.tick(4)
            if command.type_of_turn == TurnType.SMALL:
                visitedSquares += get_covered_slant_squares(robot.get_current_pos(), command.reverse)
            elif command.type_of_turn == TurnType.MEDIUM:
                pass
                # visitedSquares += get_covered_turn_squares(robot.get_current_pos(), command.reverse)
            robot.turn(command.type_of_turn, command.left, command.right, command.reverse)
            grid.draw_grid(visitedSquares)
            new_x, new_y = robot.draw_robot()

            button_image_path = get_command_for_movement(command)
            button_image = pygame.image.load(button_image_path)
            button_image = pygame.transform.scale(button_image, (30, 30))
            grid.screen.blit(button_image, (new_x,new_y))

            visitedSquares += [(init.x + i*step_size, init.y + j*step_size) for i in range(3) for j in range(3)]
            pygame.display.update()
        
        elif isinstance(command, StraightCommand):
            init = robot.get_current_pos()
            forwardCount = 0
            
            button_image_path = get_command_for_movement(command)
            button_image = pygame.image.load(button_image_path)
            button_image = pygame.transform.scale(button_image, (30, 30))
            

            while forwardCount < abs(command.dist):
                clock.tick(4)
                init = robot.get_current_pos()
                if command.dist>0:
                    robot.straight(10)
                elif command.dist<0:
                    robot.straight(-10)

                forwardCount += 10
                grid.draw_grid(visitedSquares)
                new_x, new_y = robot.draw_robot()
                grid.screen.blit(button_image, (new_x, new_y))
                visitedSquares += [(init.x + i*step_size, init.y + j*step_size) for i in range(3) for j in range(3)]
                pygame.display.update()

        elif isinstance(command, ScanCommand):
            robot.draw_robot(True)
            clock.tick(2)
            pygame.display.update()

    return 