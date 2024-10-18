import math
from typing import List, Tuple

from queue import PriorityQueue
from robot.position import RobotPosition
from robot.direction import Direction
from robot.turn_type import TurnType
from commands.command import Command
from commands.straight_command import StraightCommand
from commands.turn_command import TurnCommand

from grid import Grid


class a_star:
    def __init__(self, grid, brain, start: RobotPosition, end: RobotPosition, yolo):

        self.grid: Grid = grid.copy()
        self.brain = brain  # The Hamiltonian object
        self.start = start  # Robot Starting Position
        self.end = end  # Final Obstacle Position
        self.yolo = yolo

    def get_neighbours(
        self, pos: RobotPosition
    ) -> List[Tuple[Tuple, RobotPosition, int, Command]]:
        """
        Get movement neighbours from this position.
        Note that all values in the Position object (x, y, direction) are all with respect to the grid!
        We also expect the return Positions to be with respect to the grid.
        """
        # We assume the robot will move by 10 when travelling straight, while moving a fixed x and y value when turning
        # a fix distance of 10 when travelling straight.
        neighbours = []
        # print(f"{pos.x},{pos.y}: checking neighbors")

        # Check travel straights.
        straight_dist = 10
        straight_commands = [
            StraightCommand(straight_dist),
            StraightCommand(-straight_dist),
        ]

        for command in straight_commands:
            # Check if doing this command does not bring us to any invalid position.
            after, p = self.check_valid_command(command, pos)
            if after:
                neighbours.append((after, p, straight_dist, command))

        # Check turns
        # SOME HEURISTIC VALUE (need to account for turns travelling more also!)
        # will be adjusted on type of turn. 90 degree turn is lower cost than small turn
        turn_penalty = 100
        turn_commands = [  # type of turn, Left, Right, Reverse
            # TurnCommand(TurnType.SMALL, True, False, False),  # L SMALL turn, forward
            TurnCommand(TurnType.MEDIUM, True, False, False),  # L MEDIUM turn, forward
            # TurnCommand(TurnType.LARGE, True, False, False),  # L LARGE turn, forward
            # TurnCommand(TurnType.SMALL, True, False, True),  # L SMALL turn, reverse
            # TurnCommand(TurnType.MEDIUM, True, False, True),  # L MEDIUM turn, reverse
            # TurnCommand(TurnType.LARGE, True, False, True),  # L LARGE turn, reverse
            # TurnCommand(TurnType.SMALL, False, True, False),  # R SMALL turn, forward
            TurnCommand(TurnType.MEDIUM, False, True, False),  # R MEDIUM turn, forward
            # TurnCommand(TurnType.LARGE, False, True, False),  # R LARGE turn, forward
            # TurnCommand(TurnType.SMALL, False, True, True),  # R SMALL turn, reverse
            # TurnCommand(TurnType.MEDIUM, False, True, True),  # R MEDIUM turn, reverse
            # TurnCommand(TurnType.LARGE, False, True, True),  # R LARGE turn, reverse
        ]

        for c in turn_commands:
            # Check if doing this command does not bring us to any invalid position.
            after, p = self.check_valid_command(c, pos)

            if after:
                if c.type_of_turn == TurnType.SMALL:
                    turn_penalty = 100 if not self.yolo else 20
                elif c.type_of_turn == TurnType.MEDIUM:
                    turn_penalty = 50 if not self.yolo else 0
                neighbours.append((after, p, turn_penalty, c))

        # print("neighbours are:")
        # print(neighbours)
        return neighbours

    def check_valid_command(self, command: Command, p: RobotPosition):
        """
        Checks if a command will bring a point into any invalid position.

        If invalid, we return None for both the resulting grid location and the resulting position.
        """
        # Check specifically for validity of turn command. Robot should not exceed the grid or hit the obstacles
        p = p.copy()

        if isinstance(command, TurnCommand):
            p_c = p.copy()
            command.apply(p_c)

            # make sure that the final position is a valid one
            if not (self.grid.is_valid(p_c, self.yolo)):
                # print("Not valid position: ", p_c.x, p_c.y, p_c.direction)
                return None, None

            # if positive means the new position is to the right, else to the left side
            diff_in_x = p_c.x - p.x
            # if positive means the new position is on top of old position, else otherwise
            diff_in_y = p_c.y - p.y

            # additional check for medium turn
            # extraCheck = 1 if diff_in_x <= 30 and diff_in_y <= 30 else 0
            extraCheck = 0
            # print(f"{p.x},{p.y} ; {command} - extraCheck: {extraCheck}")

            # displace to top right
            if diff_in_y > 0 and diff_in_x > 0:
                if p.direction == Direction.TOP or p.direction == Direction.BOTTOM:
                    for y in range(0, abs(diff_in_y // 10) + extraCheck):
                        temp = p.copy()
                        temp.y += (y + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            # print(f"{p.x},{p.y} ; {command} - Position after not valid: ",
                            #       p_c.x, p_c.y, p_c.direction)
                            return None, None
                    for x in range(0, abs(diff_in_x // 10) + extraCheck):
                        temp = p_c.copy()
                        temp.x -= (x + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
                else:  # rest of the directions
                    for y in range(0, abs(diff_in_y // 10) + extraCheck):
                        temp = p_c.copy()
                        temp.y -= (y + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
                    for x in range(0, abs(diff_in_x // 10) + extraCheck):
                        temp = p.copy()
                        temp.x += (x + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
            # displace to top left
            elif diff_in_x < 0 and diff_in_y > 0:
                if p.direction == Direction.TOP or p.direction == Direction.BOTTOM:
                    for y in range(0, abs(diff_in_y // 10) + extraCheck):
                        temp = p.copy()
                        temp.y += (y + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
                    for x in range(0, abs(diff_in_x // 10) + extraCheck):
                        temp = p_c.copy()
                        temp.x += (x + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
                else:
                    for y in range(0, abs(diff_in_y // 10) + extraCheck + 1):
                        temp = p_c.copy()
                        temp.y -= (y + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
                    for x in range(0, abs(diff_in_x // 10) + extraCheck):
                        temp = p.copy()
                        temp.x -= (x + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
            # displace to bottom left
            elif diff_in_x < 0 and diff_in_y < 0:
                if p.direction == Direction.LEFT or p.direction.RIGHT:
                    for y in range(0, abs(diff_in_y // 10) + extraCheck):
                        temp = p_c.copy()
                        temp.y += (y + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
                    for x in range(0, abs(diff_in_x // 10) + extraCheck):
                        temp = p.copy()
                        temp.x -= (x + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
                else:
                    for y in range(0, abs(diff_in_y // 10) + extraCheck):
                        temp = p.copy()
                        temp.y -= (y + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
                    for x in range(0, abs(diff_in_x // 10) + extraCheck):
                        temp = p_c.copy()
                        temp.x += (x + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
            else:  # diff_in_x > 0 , diff_in_y < 0
                if p.direction == Direction.RIGHT or p.direction == Direction.LEFT:
                    for y in range(0, abs(diff_in_y // 10) + extraCheck):
                        temp = p_c.copy()
                        temp.y += (y + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
                    for x in range(0, abs(diff_in_x // 10) + extraCheck):
                        temp = p.copy()
                        temp.x += (x + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
                else:
                    for y in range(0, abs(diff_in_y // 10) + extraCheck):
                        temp = p.copy()
                        temp.y -= (y + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None
                    for x in range(0, abs(diff_in_x // 10) + extraCheck):
                        temp = p_c.copy()
                        temp.x -= (x + 1) * 10
                        if not (self.grid.is_valid(temp, self.yolo)):
                            return None, None

        command.apply(p)

        # print(f"Checking {command} from {p.x},{p.y} to {p.direction}")

        # if not (self.grid.is_valid(p, self.yolo)):
        #     print(f"Invalid position: {p.x},{p.y} to {p.direction}")

        if self.grid.is_valid(p) and (after := p.xy() + (p.get_dir(),)):
            return after, p

        return None, None

    def distance_heuristic(self, curr_pos: RobotPosition):
        """
        Measure the difference in distance between the provided position and the
        end position.
        """
        dx = abs(curr_pos.x - self.end.x)
        dy = abs(curr_pos.y - self.end.y)
        return math.sqrt(dx**2 + dy**2)

    def direction_heuristic(self, curr_pos: RobotPosition):
        """
        If not same direction as my target end position, incur penalty!
        """
        if self.end.direction == curr_pos.direction.value:
            return 0
        else:
            return 10

    def search(self, flag):
        frontier = PriorityQueue()  # Frontier Nodes
        backtrack = dict()  # Store Path
        cost = dict()  # Store Cost
        goal_node: Tuple = self.end.xy()
        goal_node_with_dir: Tuple = goal_node + (self.end.direction,)

        # Insert Start Node to list of Frontier Nodes
        start_node: Tuple = self.start.xy()
        start_node_with_dir: Tuple = start_node + (self.start.direction,)

        offset = 0  # For Tie-Breaking purposes

        frontier.put((0, offset, (start_node_with_dir, self.start)))
        cost[start_node_with_dir] = 0

        # Having None as the parent means this key is the starting node.

        backtrack[start_node_with_dir] = (None, None)  # Parent, Command

        while not frontier.empty():

            # Get the highest priority node.
            priority, _, (current_node, current_position) = frontier.get()

            # If the current node is our goal.
            if (
                current_node[0] == goal_node_with_dir[0]
                and current_node[1] == goal_node_with_dir[1]
                and current_node[2] == goal_node_with_dir[2]
            ):

                # Obtain Commands Required to reach Goal
                commands = self.extract_commands(backtrack, goal_node_with_dir, flag)

                return (current_position, commands, cost)

            # Otherwise, we go through all possible neighbours we can reach from current nodes

            neighbours = self.get_neighbours(current_position)

            for new_node, new_pos, weight, c in neighbours:
                # Weight represents cost of moving forward / turning

                # Penalise revisiting same Node
                revisit = 10 if new_node in backtrack else 0

                new_cost = cost.get(current_node) + weight + revisit

                if new_cost < cost.get(new_node, 100000):
                    offset += 1
                    priority = (
                        new_cost
                        + self.distance_heuristic(new_pos)
                        + self.direction_heuristic(new_pos)
                    )

                    # Add to Frontier Nodes list
                    frontier.put((priority, offset, (new_node, new_pos)))
                    backtrack[new_node] = (current_node, c)
                    cost[new_node] = new_cost

        # If we are here, means that there was no path that we could find.
        return (None, [], cost)

    def extract_commands(self, backtrack, goal_node, flag):
        """
        Extract required commands to get to destination.
        """
        commands = []
        curr = goal_node

        while curr:
            curr, c = backtrack.get(curr, (None, None))
            if c:
                commands.append(c)

        commands.reverse()

        if flag:
            # Add Commands to Hamiltonian Object
            self.brain.commands.extend(commands)
            return None
        else:
            return commands
