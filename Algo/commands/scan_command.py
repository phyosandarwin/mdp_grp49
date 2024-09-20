from commands.command import Command


class ScanCommand(Command):
    def __init__(self, time, obj_index):
        super().__init__(time)
        self.obj_index = obj_index

    def __str__(self):
        return f"ScanCommand(time={self.time}, obj_index={self.obj_index})"

    def process_one_tick(self, robot):
        if self.total_ticks == 0:
            return

        self.tick()

    def rpi_message(self):
        return f"P___{self.obj_index}"

    def apply(self, curr_pos):
        pass