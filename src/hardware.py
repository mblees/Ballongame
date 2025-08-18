import logging


class Pump:
    def __init__(self):
        self.logger = logging.getLogger("Pump")

    def open(self):
        pass

    def close(self):
        pass


class ReleaseValve:
    def __init__(self):
        self.logger = logging.getLogger("ReleaseValve")

    def open(self):
        pass

    def close(self):
        pass


class LED:
    def __init__(self):
        self.logger = logging.getLogger("LED")

    def set_color(self, color: tuple[int, int, int]):
        pass

    def turn_off(self):
        pass

    def turn_on(self):
        pass


class Speaker:
    def __init__(self):
        self.logger = logging.getLogger("Speaker")

    def play_sound(self, sound_id: str):
        pass

    def stop_sound(self):
        pass
