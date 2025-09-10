import logging
import board
import neopixel
import RPi.GPIO as GPIO
import pigpio
import threading
import time


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
        self._brightness = 0.6  # default full brightness

    def _apply_color(self):
        if self._state:
            scaled = tuple(int(c * self._brightness) for c in self._color)
            self.pixels[:] = [scaled] * self.num_leds
        else:
            self.pixels[:] = [(0, 0, 0)] * self.num_leds

    def set_color(self, color: tuple[int, int, int]):
        if self._color == color:
            return
        self._color = color
        self._apply_color()

    def blink(self, speed: float = 0.1, amount: int = 3):
        for i in range(amount):
            self.turn_off()
            time.sleep(speed)
            self.turn_on()
            time.sleep(speed)

    def turn_on(self):
        self._state = True
        self._apply_color()

    def turn_off(self):
        self._state = False
        self._apply_color()

    def set_brightness(self, brightness: float):
        brightness = max(0.0, min(1.0, brightness))
        if self._brightness == brightness:
            return
        self._brightness = brightness
        self._apply_color()


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
        self._stop_event = threading.Event()

    def is_pressed(self) -> bool:
        return self.pi.read(self.io) == 1

    def enable_interrupt(self, callback, poll_interval: float = 0.5):
        def _poll():
            last_state = self.is_pressed()
            while not self._stop_event.is_set():
                state = self.is_pressed()
                if state != last_state:
                    callback()
                last_state = state
                time.sleep(poll_interval)

        self._stop_event.clear()
        interrupt_thread = threading.Thread(target=_poll, daemon=True)
        interrupt_thread.start()
        return interrupt_thread

    def disable_interrupt(self):
        self._stop_event.set()
