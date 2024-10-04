import pygame
import datetime
import time
from commands.straight_command import StraightCommand
from commands.command import Command
from robot.direction import Direction
from robot.position import RobotPosition
from path_finding.hamiltonian import Hamiltonian
from commands.turn_command import TurnCommand
import constants

class Timer:
    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def end(self):
        if self.start_time is None:
            raise ValueError("Timer was not started.")
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        print(f"Total time: {elapsed_time} seconds")

class Robot:
    def __init__(self, screen, grid, x, y):
        self.pos = RobotPosition(constants.ROBOT_SAFETY_DISTANCE, constants.ROBOT_SAFETY_DISTANCE, Direction.TOP, 90)
        self._start_copy = self.pos.copy()
        self.hamiltonian = Hamiltonian(self, grid)
        self.path_hist = []
        self.__current_command = 0
        self.printed = False
        self.x = x
        self.y = y
        self.screen = screen
    
    def draw_robot(self, scan=False):
        # Starting X and Y positions of the grid
        grid_start_x = constants.TOP_BOTTOM_MARGIN
        grid_start_y = constants.TOP_BOTTOM_MARGIN
        new_x = grid_start_x + (self.pos.x // 10) * constants.CELL_SIZE
        new_y = grid_start_y + (constants.GRID_SIZE - (self.pos.y // 10) - 1) * constants.CELL_SIZE - 2* constants.CELL_SIZE

        center_x = grid_start_x + ((self.pos.x // 10) + 1) * constants.CELL_SIZE
        center_y = grid_start_y + (constants.GRID_SIZE - ((self.pos.y // 10) - 1) - 1) * constants.CELL_SIZE - 2* constants.CELL_SIZE        
        
        if not scan:
            pygame.draw.rect(self.screen, constants.YELLOW, (new_x, new_y, 3*constants.CELL_SIZE, 3*constants.CELL_SIZE))
            pygame.draw.rect(self.screen, constants.BLUE, (center_x, center_y, constants.CELL_SIZE, constants.CELL_SIZE))

        else:
            pygame.draw.rect(self.screen, constants.RED, (new_x, new_y, 3*constants.CELL_SIZE, 3*constants.CELL_SIZE))
            pygame.draw.rect(self.screen, constants.BLUE, (center_x, center_y, constants.CELL_SIZE, constants.CELL_SIZE))

        border_color = constants.RED  
        border_thickness = 5

        if self.pos.direction == Direction.TOP:
            pygame.draw.rect(self.screen, border_color, (new_x, new_y, 3*constants.CELL_SIZE, border_thickness))
        elif self.pos.direction == Direction.BOTTOM:
            pygame.draw.rect(self.screen, border_color, (new_x, new_y + 3*constants.CELL_SIZE - border_thickness, 3*constants.CELL_SIZE, border_thickness))
        elif self.pos.direction == Direction.LEFT:
            pygame.draw.rect(self.screen, border_color, (new_x, new_y, border_thickness, 3*constants.CELL_SIZE))
        elif self.pos.direction == Direction.RIGHT:
            pygame.draw.rect(self.screen, border_color, (new_x + 3*constants.CELL_SIZE - border_thickness, new_y, border_thickness, 3*constants.CELL_SIZE))

        return (new_x, new_y)
            
    ##------------
    def get_current_pos(self):
        return self.pos

    def __str__(self):
        return f"robot is at {self.pos}"

    def setCurrentPos(self, x, y, direction):
        self.pos.x = x
        self.pos.y = y 
        self.pos.direction = direction

    def setCurrentPosTask2(self, x, y, direction):
        self.pos.x = constants.TASK2_LENGTH - constants.GRID_CELL_LENGTH - (x * 10)
        self.pos.y = y * 10
        self.pos.direction = direction

    def start_algo_from_position(self, grid):
        self.pos = self.get_current_pos()
        self._start_copy = self.pos.copy()
        self.hamiltonian = Hamiltonian(self, grid)
        self.path_hist = []
        self.__current_command = 0
        self.printed = False

    def convert_all_commands(self):
        return [command.convert_to_message() for command in self.hamiltonian.commands]

    def turn(self, type_of_command, left, right, rev):
        TurnCommand(type_of_command, left, right, rev).move(self.pos)

    def straight(self, dist):
        StraightCommand(dist).move(self.pos)
    

    def draw_simple_hamiltonian_path(self, screen):
        prev = self._start_copy.xy_pygame()
        for obs in self.hamiltonian.simple_hamiltonian:
            target = obs.get_robot_target_pos().xy_pygame()
            pygame.draw.line(screen, constants.DARK_GREEN, prev, target)
            prev = target

    def draw_self(self, screen):
        rot_image = pygame.transform.rotate(self.__image, -(90 - self.pos.angle))
        rect = rot_image.get_rect()
        rect.center = self.pos.xy_pygame()
        screen.blit(rot_image, rect)

    def draw_historic_path(self, screen):
        for dot in self.path_hist:
            pygame.draw.circle(screen, constants.BLACK, dot, 2)

    def draw(self, screen):
        self.draw_self(screen)
        self.draw_simple_hamiltonian_path(screen)
        self.draw_historic_path(screen)

    def update(self):
        if len(self.path_hist) == 0 or self.pos.xy_pygame() != self.path_hist[-1]:
            self.path_hist.append(self.pos.xy_pygame())

        if self.__current_command >= len(self.hamiltonian.commands):
            return

        if self.hamiltonian.commands[self.__current_command].total_ticks == 0:
            self.__current_command += 1
            if self.__current_command >= len(self.hamiltonian.commands):
                return

        command: Command = self.hamiltonian.commands[self.__current_command]
        command.process_one_tick(self)

        if command.ticks <= 0:
            print(f"Finished processing {command}, {self.pos}")
            self.__current_command += 1
            if self.__current_command == len(self.hamiltonian.commands) and not self.printed:
                total_time = sum(command.time for command in self.hamiltonian.commands)
                total_time = round(total_time)
                print(f"All commands took {datetime.timedelta(seconds=total_time)}")
                self.printed = True
                timer.Timer.end_timer()