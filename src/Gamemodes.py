import logging
from src.Hardware import Pump, ReleaseValve, LED
import paho.mqtt.client as mqtt


class GenericGamemode:
    def __init__(self, logging_name: str, pi):
        self.logger = logging.getLogger(logging_name)
        self.mode: str = logging_name
        self.pi = pi
        self.pump = Pump(self.pi)
        self.releaseValve = ReleaseValve(self.pi)
        self.led = LED(self.pi)

        self.mqtt_client = mqtt.Client()
        self.init_mqtt_client()
        self.led.set_color((255, 0, 0))
        self.led.turn_on()

    def callback(self, client, userdata, msg):
        if msg.topic == "Pico1/Eingabe":
            self.logger.info("Encoder dreht sich")
        elif msg.topic == "Pico2/Eingabe":
            if msg.payload.decode() == "0":
                self.logger.info("Button Pressed")
        elif msg.topic == "Pico3/Eingabe":
            if msg.payload.decode() == "0":
                self.logger.info("Fan spinning")
        elif msg.topic == "Pico4/Eingabe":
            self.logger.info("Controller geschüttelt")
        else:
            pass

    def run_gameloop(self):
        self.logger.warning("Using generic Gamemode Class. Overwrite this function.")
        raise NotImplementedError()

    def print_mode(self):
        self.logger.info(f"Mode is set to: {str(self.mode)}")

    def init_mqtt_client(self):
        self.mqtt_client.username_pw_set(username="PicoNet", password="geheimespasswort")
        self.mqtt_client.connect("192.168.0.127", 1883, 60)
        self.mqtt_client.on_message = self.callback
        self.mqtt_client.subscribe("Pico1/Eingabe")
        self.mqtt_client.subscribe("Pico2/Eingabe")
        self.mqtt_client.subscribe("Pico3/Eingabe")
        self.mqtt_client.subscribe("Pico4/Eingabe")
        self.mqtt_client.loop_start()


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
