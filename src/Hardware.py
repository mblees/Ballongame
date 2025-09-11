import logging
import board
import neopixel
import RPi.GPIO as GPIO
import pigpio
import threading
import time
import math
import random


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
        self._brightness = 0.3  # default full brightness

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

    def sinus(self, period: float = 0.5, cycles: int = 3, steps: int = 15):
        brightness_before = self._brightness
        self._state = True
        for _ in range(cycles):
            for i in range(steps):
                angle = (i / steps) * 2 * math.pi
                self._brightness = 0.5 * (1 - math.cos(angle))  # sine wave 0..1
                self._apply_color()
                time.sleep(period / steps)
        self.set_brightness(brightness_before)

    def sparkle(self, duration: float = 3.0, chance: float = 0.2, interval: float = 0.05):
        end_time = time.time() + duration
        self._state = True
        base_color = (0, 0, 0)

        while time.time() < end_time:
            frame = []
            for _ in range(self.num_leds):
                if random.random() < chance:
                    sparkle_color = tuple(min(255, int(c * random.uniform(0, self._brightness))) for c in self._color)
                    frame.append(sparkle_color)
                else:
                    frame.append(base_color)
            self.pixels[:] = frame
            time.sleep(interval)

    def load_bar(self, delay: float = 0.025):
        self._state = True
        r, g, b = self._color
        r *= self._brightness
        g *= self._brightness
        b *= self._brightness
        self.set_color((0, 0, 0))
        for i in range(self.num_leds):
            self.pixels[i] = (r, g, b)
            time.sleep(delay)

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
        self.pi.set_mode(self.io, 0)  # 0 = INPUT

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


class MiuzeiDigitalServo:  # 20kg Servo
    def __init__(self, pi, io: int, min_angle: float = 0.0, max_angle: float = 270.0,
                 min_pulse: int = 500, max_pulse: int = 2500):
        self.logger = logging.getLogger("MiuzeiDigitalServo")
        self.pi = pi
        self.io = io
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.current_angle = None

        self.eject_angle = 130
        self.normal_angle = 180

        # Set GPIO as output (pigpio handles PWM on it)
        self.pi.set_mode(self.io, 1)  # 1 = OUTPUT

    def _angle_to_pulse(self, angle: float) -> int:
        angle = max(self.min_angle, min(self.max_angle, angle))  # clamp
        pulse = int(self.min_pulse + (angle - self.min_angle) *
                    (self.max_pulse - self.min_pulse) / (self.max_angle - self.min_angle))
        return pulse

    def rotate_to(self, angle: float):
        self.logger.debug(f"moving servo to angle {angle}")
        pulse = self._angle_to_pulse(angle)
        self.logger.debug(f"Rotating to {angle:.1f}° → pulse {pulse}µs")
        self.pi.set_servo_pulsewidth(self.io, pulse)
        self.current_angle = angle
        time.sleep(1)  # give servo time to move
        self.stop()

    def stop(self):
        self.logger.debug("Stopping servo PWM output")
        self.pi.set_servo_pulsewidth(self.io, 0)

    def eject(self):
        self.rotate_to(self.eject_angle)

    def reset(self):
        self.rotate_to(self.normal_angle)

    def eject_and_reset(self):
        self.logger.debug("Eject and reset triggered!")
        self.eject()
        time.sleep(1)
        self.reset()
