import logging
import board
import neopixel
import RPi.GPIO as GPIO
import pigpio


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
    def __init__(self, pi, num_leds: int = 1):
        self.logger = logging.getLogger("LED")
        self.pin = board.D18
        self.pi = pi
        self.num_leds = num_leds
        self.pixels = neopixel.NeoPixel(self.pin, num_leds, auto_write=True)
        self._color = (0, 0, 0)
        self._state = False

    def set_color(self, color: tuple[int, int, int]):
        if self._color == color:
            return  # No need to set the same color again
        self._color = color
        if self._state:
            for i in range(self.num_leds):
                self.pixels[i] = color

    def turn_off(self):
        self._state = False
        for i in range(self.num_leds):
            self.pixels[i] = (0, 0, 0)

    def turn_on(self):
        self._state = True
        for i in range(self.num_leds):
            self.pixels[i] = self._color


class Speaker:
    def __init__(self):
        self.logger = logging.getLogger("Speaker")

    def play_sound(self, sound_id: str):
        pass

    def stop_sound(self):
        pass


class Button:
    def __init__(self, pi, io: int):
        self.logger = logging.getLogger("Button")
        self.io = io
        self.pi = pi

    def is_pressed(self) -> bool:
        return self.pi.read(self.io) == 1

    def enable_interrupt(self, callback):
        self.pi.callback(self.io, pigpio.RISING_EDGE, callback)

