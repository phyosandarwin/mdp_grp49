from abc import ABC, abstractmethod
import constants

class Command(ABC):
    def __init__(self, time):
        self.time = time
        self.ticks = int(time * constants.FRAMES)
        self.total_ticks = self.ticks

    def tick(self):
        self.ticks -= 1

    @abstractmethod
    def process_one_tick(self, robot):
        self.tick()

    @abstractmethod
    def rpi_message(self):
        """
        Conversion to a message that is easy to send over the RPi.
        """
        pass

    @abstractmethod
    def apply(self, curr_pos):
        """
        Apply this command to a Position, such that its attributes will reflect the correct values
        after the command is done.

        This method should return itself.
        """
        pass
