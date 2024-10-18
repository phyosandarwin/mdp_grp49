import itertools
import math
from typing import Tuple
from collections import deque
from commands.scan_command import ScanCommand
from commands.straight_command import StraightCommand
from commands.turn_command import TurnCommand
from robot.direction import Direction
from grid import Grid
from obstacle import Obstacle
from path_finding.a_star import a_star
from robot.position import Position
import constants


class Hamiltonian:

    def __init__(self, robot, grid: Grid):
        self.robot = robot
        self.grid = grid
        self.path = tuple()
        self.commands = deque()

    def get_path(self):
        return self.path

    def compute_path(self) -> Tuple[Obstacle]:
        perms = list(itertools.permutations(self.grid.obstacles))

        def calc_distance(path):

            # Checks if Robot must turn Left or Right depending on the Target Position
            def check_turn(robot_pos, target_pos):
                if (
                    robot_pos.direction.value - target_pos.direction.value == -90
                ):  # left turn
                    if robot_pos.direction == Direction.TOP:
                        return True if target_pos.x < robot_pos.x else False
                    if robot_pos.direction == Direction.BOTTOM:
                        return True if target_pos.x > robot_pos.x else False
                    if robot_pos.direction == Direction.LEFT:
                        return True if target_pos.y < robot_pos.y else False
                    if robot_pos.direction == Direction.RIGHT:
                        return True if target_pos.y > robot_pos.y else False
                else:  # turn right
                    if robot_pos.direction == Direction.TOP:
                        return True if target_pos.x > robot_pos.x else False
                    if robot_pos.direction == Direction.BOTTOM:
                        return True if target_pos.x < robot_pos.x else False
                    if robot_pos.direction == Direction.LEFT:
                        return True if target_pos.y > robot_pos.y else False
                    if robot_pos.direction == Direction.RIGHT:
                        return True if target_pos.y < robot_pos.y else False

            # The multiplier is determined based on the direction change between the source and destination.
            # If they have the same direction, the multiplier is 1 or 5.
            # If they have opposite directions, the multiplier is 3.
            # If they require a left/right turn, the multiplier is 1.5 or 7 depending on whether it is a "natural" turn direction or not.

            # Multiplier for 5 (120, 40) to 3 (150, 90) is 3, Euclidean = 58.3
            # Multiplier for (120, 40) to (150, 120) is 1.5, Euclidean = 85

            def get_weight(source_pos, dest_pos, is_first) -> int:
                if source_pos.direction.value - dest_pos.direction.value == 0:
                    weight = 1 if is_first else 5  # facing each other
                elif abs(source_pos.direction.value - dest_pos.direction.value) == 180:
                    weight = 1.5  # opposite directions
                else:
                    weight = 3 if check_turn(source_pos, dest_pos) else 7

                # print(f"Weight from {source_pos} to {dest_pos} is {weight}")
                return weight

            def euclidean_distance(x1, y1, x2, y2):
                return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

            def manhattan_distance(x1, y1, x2, y2):
                return abs(x1 - x2) + abs(y1 - y2)

            distance = 0
            multiplier = 1
            targets = [self.robot.pos.xy()]

            for obstacle in path:
                targets.append(obstacle.target.xy())

            for i in range(len(targets) - 1):
                if i == 0:
                    multiplier = get_weight(self.robot.pos, path[i].target, True)
                else:
                    multiplier = get_weight(path[i - 1].target, path[i].target, False)

                distance += multiplier * euclidean_distance(
                    targets[i][0], targets[i][1], targets[i + 1][0], targets[i + 1][1]
                )
            #     print(f"Multiplier for {targets[i]} to {targets[i + 1]} is {multiplier}")
            #     print(f"Euclidean Distance from {targets[i]} to {targets[i + 1]} is {euclidean_distance(targets[i][0], targets[i][1], targets[i + 1][0], targets[i + 1][1])}")

            # print(f"Weighted Distance for {path} is {distance}")
            return distance

        print("Getting distance for every permutation")

        simple = min(perms, key=calc_distance)

        print("Found Hamiltonian path\n")

        for ob in simple:
            print(
                f"\tObstacle {ob.number} at {ob.position.xy()} -> Robot should go to {ob.target.xy()}"
            )

        return simple

    def compress_straights(self):
        """
        Check if Multiple Straight Commands can be compresultsed into one
        """
        print("Compressing commands...", end="")
        index = 0
        new_commands = deque()

        while index < len(self.commands):
            command = self.commands[index]

            # Combine multiple straight commands into one by summing up their lengths
            if isinstance(command, StraightCommand):
                new_length = 0
                while index < len(self.commands) and isinstance(
                    self.commands[index], StraightCommand
                ):
                    new_length += self.commands[index].dist
                    index += 1
                command = StraightCommand(new_length)
                new_commands.append(command)
            else:
                new_commands.append(command)
                index += 1

        self.commands = new_commands
        print("Done!")

    def compute_path_(self):
        perms = list(itertools.permutations(self.grid.obstacles))
        best_i = -1
        best_cost = 999999999
        costs = [[-1 for _ in range(6)] for _ in range(6)]

        for i in range(len(perms)):
            obstacles = perms[i]
            cobs = None
            curr = self.robot.pos.copy()
            cost = 0
            # compute cost
            for j in range(len(obstacles)):
                obstacle = obstacles[j]
                # check if found
                if cobs == None:
                    cobs = obstacle
                curr_cost = costs[int(cobs.number) - 1][int(obstacle.number) - 1]
                # found
                if curr_cost != -1:
                    cobs = obstacle
                    curr = obstacle.get_robot_position()
                    cost += curr_cost
                    continue
                # not found
                target = obstacle.get_robot_position()
                attempt = 0  # Tracking attempts
                result, _, curr_costs = a_star(
                    self.grid, self, curr, target, attempt
                ).search(False)
                while result is None and attempt != 2:
                    attempt += 1
                    result, _, curr_costs = a_star(
                        self.grid, self, curr, target, attempt
                    ).search(False)
                    if result:
                        break
                if result is None:
                    cost += 9999
                else:
                    curr_cost = curr_costs[
                        obstacle.get_robot_position().xy()
                        + (obstacle.get_robot_position().direction,)
                    ]
                    costs[int(cobs.number) - 1][int(obstacle.number) - 1] = curr_cost
                    cobs = obstacle
                    curr = result
                    cost += curr_cost
            if cost < best_cost:
                best_cost = cost
                best_i = i

        for ob in perms[best_i]:
            print(
                f"\tObstacle {ob.number} at {ob.position.xy()} -> Robot should go to {ob.target.xy()}"
            )
        return perms[best_i]

    def get_path(self):
        # self.compute_path_()
        print("-" * 40)
        print("Getting Simple Hamiltonian Path...")
        self.simple_hamiltonian = self.compute_path_()
        print()

        curr = self.robot.pos.copy()

        # Following order of obstacles determined in Simple Hamiltonian
        targets = []

        for obstacle in self.simple_hamiltonian:
            targets.append(obstacle.get_robot_position())

        for obstacle in self.simple_hamiltonian:

            target = obstacle.get_robot_position()

            attempt = 0  # Tracking attempts

            result, commands, cost = a_star(
                self.grid, self, curr, target, attempt
            ).search(True)

            while result is None and attempt != 2:
                print(f"No path from {curr} to {obstacle.number}.")
                print("Trying again...", end=" ")

                attempt += 1
                result, commands, cost = a_star(
                    self.grid, self, curr, target, attempt
                ).search(True)

                if result:
                    break

            if result is None:
                print(f"No path from {curr} to {obstacle.number}.")

            else:
                print(f"Shortest Path found from {curr} to {obstacle.number}")
                curr = result
                self.commands.append(
                    ScanCommand(constants.ROBOT_SCAN_DURATION, obstacle.number)
                )

        self.compress_straights()

        print("-" * 40)

        if len(self.commands) == 0:
            print("No path found.")
            return
        for command in self.commands:
            print(f"{command}")

        print("-" * 40)
        print()
