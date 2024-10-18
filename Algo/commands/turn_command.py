from commands.command import Command
from robot.turn_type import TurnType
from robot.direction import Direction
from robot.position import Position, RobotPosition


class TurnCommand(Command):
    SMALL_TURN_TIME = 10
    MEDIUM_TURN_TIME = 20
    LARGE_TURN_TIME = 30

    # change in coords facing north
    fr1, fr2 = 30, 20
    fl1, fl2 = 30, 20
    br1, br2 = 30, 30
    bl1, bl2 = 20, 30

    def __init__(self, type_of_turn, left, right, reverse):
        turn_time = {
            TurnType.SMALL: TurnCommand.SMALL_TURN_TIME,
            TurnType.MEDIUM: TurnCommand.MEDIUM_TURN_TIME,
            TurnType.LARGE: TurnCommand.LARGE_TURN_TIME,
        }
        super().__init__(turn_time[type_of_turn])
        self.type_of_turn = type_of_turn
        self.left = left
        self.right = right
        self.reverse = reverse

    def __str__(self):
        return f"TurnCommand:{self.type_of_turn}, rev={self.reverse}, left={self.left}, right={self.right})"

    def process_one_tick(self, robot):
        if self.total_ticks == 0:
            return

        self.tick()
        robot.turn(self.type_of_turn, self.left, self.right, self.reverse)

    def move(self, curr_pos: Position):
        assert isinstance(
            curr_pos, RobotPosition
        ), "Cannot apply turn command on non-robot positions!"

        # fl
        if self.left and not self.right and not self.reverse:
            if self.type_of_turn == TurnType.MEDIUM:
                if curr_pos.direction == Direction.TOP:
                    curr_pos.x -= TurnCommand.fl1
                    curr_pos.y += TurnCommand.fl2
                    curr_pos.direction = Direction.LEFT
                elif curr_pos.direction == Direction.BOTTOM:
                    curr_pos.x += TurnCommand.fl1
                    curr_pos.y -= TurnCommand.fl2
                    curr_pos.direction = Direction.RIGHT
                elif curr_pos.direction == Direction.LEFT:
                    curr_pos.x -= TurnCommand.fl2
                    curr_pos.y -= TurnCommand.fl1
                    curr_pos.direction = Direction.BOTTOM
                elif curr_pos.direction == Direction.RIGHT:
                    curr_pos.x += TurnCommand.fl2
                    curr_pos.y += TurnCommand.fl1
                    curr_pos.direction = Direction.TOP

        # fr
        if self.right and not self.left and not self.reverse:
            if self.type_of_turn == TurnType.MEDIUM:
                if curr_pos.direction == Direction.TOP:
                    curr_pos.x += TurnCommand.fr1
                    curr_pos.y += TurnCommand.fr2
                    curr_pos.direction = Direction.RIGHT
                elif curr_pos.direction == Direction.BOTTOM:
                    curr_pos.x -= TurnCommand.fr1
                    curr_pos.y -= TurnCommand.fr2
                    curr_pos.direction = Direction.LEFT
                elif curr_pos.direction == Direction.LEFT:
                    curr_pos.x -= TurnCommand.fr2
                    curr_pos.y += TurnCommand.fr1
                    curr_pos.direction = Direction.TOP
                elif curr_pos.direction == Direction.RIGHT:
                    curr_pos.x += TurnCommand.fr2
                    curr_pos.y -= TurnCommand.fr1
                    curr_pos.direction = Direction.BOTTOM

        # bl
        if self.left and not self.right and self.reverse:
            if self.type_of_turn == TurnType.MEDIUM:
                if curr_pos.direction == Direction.TOP:
                    curr_pos.x -= TurnCommand.bl1
                    curr_pos.y -= TurnCommand.bl2
                    curr_pos.direction = Direction.RIGHT
                elif curr_pos.direction == Direction.BOTTOM:
                    curr_pos.x += TurnCommand.bl1
                    curr_pos.y += TurnCommand.bl2
                    curr_pos.direction = Direction.LEFT
                elif curr_pos.direction == Direction.LEFT:
                    curr_pos.x += TurnCommand.bl2
                    curr_pos.y -= TurnCommand.bl1
                    curr_pos.direction = Direction.TOP
                elif curr_pos.direction == Direction.RIGHT:
                    curr_pos.x -= TurnCommand.bl2
                    curr_pos.y += TurnCommand.bl1
                    curr_pos.direction = Direction.BOTTOM

        # br
        if self.right and not self.left and self.reverse:
            if self.type_of_turn == TurnType.MEDIUM:
                if curr_pos.direction == Direction.TOP:
                    curr_pos.x += TurnCommand.br1
                    curr_pos.y -= TurnCommand.br2
                    curr_pos.direction = Direction.LEFT
                elif curr_pos.direction == Direction.BOTTOM:
                    curr_pos.x -= TurnCommand.br1
                    curr_pos.y += TurnCommand.br2
                    curr_pos.direction = Direction.RIGHT
                elif curr_pos.direction == Direction.LEFT:
                    curr_pos.x += TurnCommand.br2
                    curr_pos.y += TurnCommand.br1
                    curr_pos.direction = Direction.BOTTOM
                elif curr_pos.direction == Direction.RIGHT:
                    curr_pos.x -= TurnCommand.br2
                    curr_pos.y -= TurnCommand.br1
                    curr_pos.direction = Direction.TOP

        return self

    def apply(self, curr_pos: Position):
        """
        changes the robot position according to what command it is and where the robot is currently at
        """
        assert isinstance(curr_pos, RobotPosition), print(
            "Cannot apply turn command on non-robot positions!"
        )

        # Get change in (x, y) coordinate.

        # turn left and forward
        if self.left and not self.right and not self.reverse:
            if self.type_of_turn == TurnType.MEDIUM:
                if curr_pos.direction == Direction.TOP:
                    curr_pos.x -= TurnCommand.fl1
                    curr_pos.y += TurnCommand.fl2
                    curr_pos.direction = Direction.LEFT
                elif curr_pos.direction == Direction.BOTTOM:
                    curr_pos.x += TurnCommand.fl1
                    curr_pos.y -= TurnCommand.fl2
                    curr_pos.direction = Direction.RIGHT
                elif curr_pos.direction == Direction.LEFT:
                    curr_pos.x -= TurnCommand.fl2
                    curr_pos.y -= TurnCommand.fl1
                    curr_pos.direction = Direction.BOTTOM
                elif curr_pos.direction == Direction.RIGHT:
                    curr_pos.x += TurnCommand.fl2
                    curr_pos.y += TurnCommand.fl1
                    curr_pos.direction = Direction.TOP

        # turn right and forward
        if self.right and not self.left and not self.reverse:
            if self.type_of_turn == TurnType.MEDIUM:
                if curr_pos.direction == Direction.TOP:
                    curr_pos.x += TurnCommand.fr1
                    curr_pos.y += TurnCommand.fr2
                    curr_pos.direction = Direction.RIGHT
                elif curr_pos.direction == Direction.BOTTOM:
                    curr_pos.x -= TurnCommand.fr1
                    curr_pos.y -= TurnCommand.fr2
                    curr_pos.direction = Direction.LEFT
                elif curr_pos.direction == Direction.LEFT:
                    curr_pos.x -= TurnCommand.fr2
                    curr_pos.y += TurnCommand.fr1
                    curr_pos.direction = Direction.TOP
                elif curr_pos.direction == Direction.RIGHT:
                    curr_pos.x += TurnCommand.fr2
                    curr_pos.y -= TurnCommand.fr1
                    curr_pos.direction = Direction.BOTTOM

        # turn front wheels left and reverse
        if self.left and not self.right and self.reverse:
            if self.type_of_turn == TurnType.MEDIUM:
                if curr_pos.direction == Direction.TOP:
                    curr_pos.x -= TurnCommand.bl1
                    curr_pos.y -= TurnCommand.bl2
                    curr_pos.direction = Direction.RIGHT
                elif curr_pos.direction == Direction.BOTTOM:
                    curr_pos.x += TurnCommand.bl1
                    curr_pos.y += TurnCommand.bl2
                    curr_pos.direction = Direction.LEFT
                elif curr_pos.direction == Direction.LEFT:
                    curr_pos.x += TurnCommand.bl2
                    curr_pos.y -= TurnCommand.bl1
                    curr_pos.direction = Direction.TOP
                elif curr_pos.direction == Direction.RIGHT:
                    curr_pos.x -= TurnCommand.bl2
                    curr_pos.y += TurnCommand.bl1
                    curr_pos.direction = Direction.BOTTOM

        # turn front wheels right and reverse
        if self.right and not self.left and self.reverse:
            if self.type_of_turn == TurnType.MEDIUM:
                if curr_pos.direction == Direction.TOP:
                    curr_pos.x += TurnCommand.br1
                    curr_pos.y -= TurnCommand.br2
                    curr_pos.direction = Direction.LEFT
                elif curr_pos.direction == Direction.BOTTOM:
                    curr_pos.x -= TurnCommand.br1
                    curr_pos.y += TurnCommand.br2
                    curr_pos.direction = Direction.RIGHT
                elif curr_pos.direction == Direction.LEFT:
                    curr_pos.x += TurnCommand.br2
                    curr_pos.y += TurnCommand.br1
                    curr_pos.direction = Direction.BOTTOM
                elif curr_pos.direction == Direction.RIGHT:
                    curr_pos.x -= TurnCommand.br2
                    curr_pos.y -= TurnCommand.br1
                    curr_pos.direction = Direction.TOP

        return self

    # FR
    # cmds = {'commands': 'B010,FR90,B012'}
    # FL
    # cmds = {'commands': 'B006,FL90,B007'}
    # BL
    # cmds = {'commands': 'F005,BL90,B005'}
    # BR
    # cmds = {'commands': 'F013,BR90,B005'}

    def rpi_message(self):
        if self.left and not self.right and not self.reverse:
            if self.type_of_turn == TurnType.SMALL:
                return "KF000"
            elif self.type_of_turn == TurnType.MEDIUM:
                return "SF005,LF090,SB005"
            elif self.type_of_turn == TurnType.LARGE:
                return "LF180"
        elif self.left and not self.right and self.reverse:
            if self.type_of_turn == TurnType.SMALL:
                return "KB000"
            elif self.type_of_turn == TurnType.MEDIUM:
                return "SF005,LB090,SB005"
            elif self.type_of_turn == TurnType.LARGE:
                return "LB180"
        elif self.right and not self.left and not self.reverse:
            if self.type_of_turn == TurnType.SMALL:
                return "JF000"
            elif self.type_of_turn == TurnType.MEDIUM:
                return "SB010,RF090,SB012"
            elif self.type_of_turn == TurnType.LARGE:
                return "RF180"
        else:
            if self.type_of_turn == TurnType.SMALL:
                return "JB000"
            elif self.type_of_turn == TurnType.MEDIUM:
                return "SF013,RB180,SB005"
            elif self.type_of_turn == TurnType.LARGE:
                return "RB180"
