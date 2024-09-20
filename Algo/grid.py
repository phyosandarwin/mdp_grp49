import pygame
import constants    
from robot.position import Position

class Grid:
    def __init__(self, screen, obstacles):
        self.screen = screen
        self.obstacles = obstacles

    def copy(self):
        """
        Return a copy of the grid.
        """

        grid_copy = Grid(self.screen,self.obstacles)
        
        return grid_copy

    
    def draw_grid(self, visitedSquares):
        
        grid_start_x, grid_start_y = constants.TOP_BOTTOM_MARGIN, constants.TOP_BOTTOM_MARGIN
        grid_end_x, grid_end_y = grid_start_x + constants.GRID_PIXEL_SIZE, grid_start_y + constants.GRID_PIXEL_SIZE
        
        self.color_cells(visitedSquares, (0,255,0))

        for i in range(constants.GRID_SIZE + 1):
            start_x = grid_start_x + i * constants.CELL_SIZE
            start_y = grid_start_y + i * constants.CELL_SIZE
            color = (0, 0, 0)
            if i == 0 or i == constants.GRID_SIZE:
                color = (255, 0, 0)
            pygame.draw.line(self.screen, color, (start_x, grid_start_y), (start_x, grid_end_y))
            pygame.draw.line(self.screen, color, (grid_start_x, start_y), (grid_end_x, start_y))
        for obstacle in self.obstacles:
            obstacle.draw_obstacle()
        

    def is_valid(self, pos: Position, yolo=False):
        """
        Check if a current position can be here.
        """
        # Check if current position is at an obstacle.
        if any(obstacle.is_safe(pos, yolo) for obstacle in self.obstacles):
            # print("Obstacle")
            return False

        # Check if we are out of grid bounds
        if (pos.y < constants.CELL_LENGTH or pos.y >= constants.GRID_SIZE*10 - constants.CELL_LENGTH) or (pos.x < constants.CELL_LENGTH or pos.x >= constants.GRID_SIZE*10 - constants.CELL_LENGTH):

            # print(pos.y < constants.CELL_LENGTH, pos.y >= constants.GRID_SIZE*10 - constants.CELL_LENGTH)
            # print(pos.x < constants.CELL_LENGTH, pos.x >= constants.GRID_SIZE*10 - constants.CELL_LENGTH)
                        
            # print("Out of bounds " + str(pos.x) + " " + str(pos.y))
            return False
        return True
    
    def color_cells(self, cell_coordinates, color):
        grid_start_x, grid_start_y = constants.TOP_BOTTOM_MARGIN, constants.TOP_BOTTOM_MARGIN
        for x, y in cell_coordinates:
            new_x = grid_start_x + (x // 10) * constants.CELL_SIZE
            new_y = grid_start_y + (constants.GRID_SIZE - (y // 10) - 1) * constants.CELL_SIZE
            pygame.draw.rect(self.screen, color, (new_x, new_y, constants.CELL_SIZE, constants.CELL_SIZE))