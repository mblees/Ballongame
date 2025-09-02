import logging
from src.Hardware import Pump, ReleaseValve, LED


class GenericGamemode:
    def __init__(self, logging_name: str, pi):
        self.logger = logging.getLogger(logging_name)
        self.mode: str = logging_name
        self.pi = pi
        self.pump = Pump(self.pi)
        self.releaseValve = ReleaseValve(self.pi)
        self.LED = LED(self.pi)

    def run_gameloop(self):
        self.logger.warning("Using generic Gamemode Class. Overwrite this function.")
        raise NotImplementedError()

    def print_mode(self):
        self.logger.info(f"Mode is set to: {str(self.mode)}")


class EasyMode(GenericGamemode):
    def __init__(self, pi):
        super().__init__("Easy Mode", pi)

    def run_gameloop(self):
        pass


class MediumMode(GenericGamemode):
    def __init__(self, pi):
        super().__init__("Medium Mode", pi)

    def run_gameloop(self):
        pass


class HardMode(GenericGamemode):
    def __init__(self, pi):
        super().__init__("Hard Mode", pi)

    def run_gameloop(self):
        pass
