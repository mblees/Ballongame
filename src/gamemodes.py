import logging


class GenericGamemode:
    def __init__(self, logging_name: str):
        self.logger = logging.getLogger(logging_name)

    def run_gameloop(self):
        self.logger.warning("Using generic Gamemode Class. Overwrite this function.")


class EasyMode(GenericGamemode):
    def __init__(self):
        super().__init__("Easy Mode")

    def run_gameloop(self):
        pass


class MediumMode(GenericGamemode):
    def __init__(self):
        super().__init__("Medium Mode")

    def run_gameloop(self):
        pass

class HardMode(GenericGamemode):
    def __init__(self):
        super().__init__("Hard Mode")

    def run_gameloop(self):
        pass