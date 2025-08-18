import logging
import time

from logging_config import activate_logging_config

from src.gamemodes import Modes, GenericGamemode, EasyMode, MediumMode, HardMode


class Ballongame:
    def __init__(self):
        self.logger = logging.getLogger("Ballongame")
        self.logger.setLevel(logging.DEBUG)
        self.mode: GenericGamemode = EasyMode()
        self._running = True

    def run(self):
        self.logger.info("Starting Game Loop!")
        while self._running:
            self.mode.print_mode()
            self.change_mode()
            time.sleep(2)

    def change_mode(self):
        if isinstance(self.mode, EasyMode):
            self.mode = MediumMode()
        elif isinstance(self.mode, MediumMode):
            self.mode = HardMode()
        elif isinstance(self.mode, HardMode):
            self.mode = EasyMode()


if __name__ == "__main__":
    activate_logging_config()
    ballongame = Ballongame()
    ballongame.run()
