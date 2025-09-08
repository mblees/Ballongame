import logging
import board
import neopixel


class Pump:
    def __init__(self, pi):
        self.logger = logging.getLogger("Pump")
        self.io = 17
        self.pi = pi

    def open(self):
        self.pi.write(self.io, 1)

    def close(self):
        self.pi.write(self.io, 0)


class ReleaseValve:
    def __init__(self, pi):
        self.logger = logging.getLogger("ReleaseValve")
        self.io = 27
        self.pi = pi

    def open(self):
        self.pi.write(self.io, 1)

    def close(self):
        self.pi.write(self.io, 0)


class LED:
    def __init__(self, pi):
        self.logger = logging.getLogger("LED")
        self.pin = board.D18
        self.pi = pi
        self.pixels = neopixel.NeoPixel(self.pin, 100, auto_write=True)
        self._color = (0, 0, 0)
        self._state = False

    def set_color(self, color: tuple[int, int, int]):
        self._color = color
        if self._state:
            self.pixels[0] = color

    def turn_off(self):
        self._state = False
        self.pixels[0] = (0, 0, 0)

    def turn_on(self):
        self._state = True
        self.pixels[0] = self._color


class Speaker:
    def __init__(self):
        self.logger = logging.getLogger("Speaker")

    def play_sound(self, sound_id: str):
        pass

    def stop_sound(self):
        pass
