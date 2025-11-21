import logging
import time

from logging_config import activate_logging_config

from src.Gamemodes import GenericGamemode, EasyMode, MediumMode, HardMode, GamemodeTools
import RPi.GPIO as GPIO
import pigpio
from src.Hardware import Button


class Ballongame:
    def __init__(self):
        self.logger = logging.getLogger("Ballongame")
        self.logger.setLevel(logging.DEBUG)
        
        self.logger.info("Initializing Ballongame...")

        self.pi = pigpio.pi()
        GPIO.setmode(GPIO.BCM)

        self.tools = GamemodeTools()
        self.mode: GenericGamemode = EasyMode(self.pi, self.tools)
        self.mode_button = Button(self.pi, 22)
        self.mode_button.enable_interrupt(self.change_mode)
        self._running = True
        self._pause = False
        

    def run(self):
        self.logger.info("Starting Game Loop!")
        while self._running:
            if not self._pause:
                self.mode.run_gameloop()

    def change_mode(self):
        if not self.mode.first_cycle:
            self._pause = True
            self.mode.cleanup()
            
            if isinstance(self.mode, EasyMode):
                self.mode = MediumMode(self.pi, self.tools)
                self.logger.info("Changing Mode to MediumMode!")
            elif isinstance(self.mode, MediumMode):
                self.mode = HardMode(self.pi, self.tools)
                self.logger.info("Changing Mode to HardMode!")
            elif isinstance(self.mode, HardMode):
                self.mode = EasyMode(self.pi, self.tools)
                self.logger.info("Changing Mode to EasyMode!")
                
            time.sleep(3) # Time for the last loop to finish
            self._pause = False


if __name__ == "__main__":
    activate_logging_config()
    ballongame = Ballongame()
    ballongame.run()
