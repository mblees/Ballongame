import logging
import time

from logging_config import activate_logging_config

from src.Gamemodes import GenericGamemode, EasyMode, MediumMode, HardMode
import RPi.GPIO as GPIO
import pigpio
from src.Hardware import Button


class Ballongame:
    def __init__(self):
        self.logger = logging.getLogger("Ballongame")
        self.logger.setLevel(logging.DEBUG)

        self.pi = pigpio.pi()
        GPIO.setmode(GPIO.BCM)

        self.mode: GenericGamemode = EasyMode(self.pi)
        self.mode_button = Button(27, self.pi)
        self.mode_button.enable_interrupt(self.change_mode)
        self._running = True

    def run(self):
        self.logger.info("Starting Game Loop!")
        while self._running:
            self.mode.run_gameloop()

    def change_mode(self):
        if isinstance(self.mode, EasyMode):
            self.mode = MediumMode(self.pi)
        elif isinstance(self.mode, MediumMode):
            self.mode = HardMode(self.pi)
        elif isinstance(self.mode, HardMode):
            self.mode = EasyMode(self.pi)


if __name__ == "__main__":
    activate_logging_config()
    ballongame = Ballongame()
    ballongame.run()
