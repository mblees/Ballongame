import logging
from src.Hardware import Pump, ReleaseValve, LED
import paho.mqtt.client as mqtt
import time
import socket

class GenericGamemode:
    def __init__(self, logging_name: str, pi):
        self.logger = logging.getLogger(logging_name)
        self.mode: str = logging_name
        self.pi = pi
        self.pump = Pump(self.pi)
        self.releaseValve = ReleaseValve(self.pi)
        self.led = LED(self.pi, num_leds=100)
        self.logger.debug("Initializing Game Mode!")

        self.mqtt_client = mqtt.Client()
        self.wait_for_network()
        self.init_mqtt_client()
        self.led.set_color((255, 0, 0))
        self.led.turn_on()

    def callback(self, client, userdata, msg):
        if msg.payload.decode() == "0":
            if msg.topic == "Pico1/Eingabe":
                self.logger.info("Encoder dreht sich")
                self.led.set_color((255, 0, 0))
            elif msg.topic == "Pico2/Eingabe":
                self.logger.info("Button Pressed")
                self.led.set_color((0, 255, 0))
            elif msg.topic == "Pico3/Eingabe":
                self.logger.info("Fan spinning")
                self.led.set_color((0, 0, 255))
            elif msg.topic == "Pico4/Eingabe":
                self.logger.info("Controller geschüttelt")
                self.led.set_color((255, 0, 255))
            else:
                pass

    def run_gameloop(self):
        self.logger.warning("Using generic Gamemode Class. Overwrite this function.")
        raise NotImplementedError()

    def print_mode(self):
        self.logger.info(f"Mode is set to: {str(self.mode)}")

    def init_mqtt_client(self):
        self.mqtt_client.username_pw_set(username="PicoNet", password="geheimespasswort")
        connected = False
        while not connected:
            try:
                self.mqtt_client.connect("192.168.4.1", 1883, 60)
                connected = True
            except Exception as e:
                print(f"Connection failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)

        self.mqtt_client.on_message = self.callback
        self.mqtt_client.subscribe("Pico1/Eingabe")
        self.mqtt_client.subscribe("Pico2/Eingabe")
        self.mqtt_client.subscribe("Pico3/Eingabe")
        self.mqtt_client.subscribe("Pico4/Eingabe")
        self.mqtt_client.loop_start()

    def wait_for_network(self, host="8.8.8.8", port=53, timeout=3, retries=10):
        """Wait until the network is reachable."""
        while True:
            try:
                socket.create_connection((host, port), timeout=timeout)
                self.logger.info("Network is reachable.")
                return True
            except OSError:
                self.logger.warning(f"Network unreachable, retrying...")
                time.sleep(3)


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
