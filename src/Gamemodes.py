import logging
from src.Hardware import Pump, ReleaseValve, LED, MiuzeiDigitalServo
import paho.mqtt.client as mqtt
import time
import socket
import random


class GenericGamemode:
    def __init__(self, logging_name: str, pi):
        self.logger = logging.getLogger(logging_name)
        self.mode: str = logging_name
        self.pi = pi
        self.pump = Pump(self.pi)
        self.releaseValve = ReleaseValve(self.pi)
        self.led = LED(self.pi, num_leds=75)
        self.servo = MiuzeiDigitalServo(self.pi, 13)
        self.servo.eject()

        self.mqtt_client = mqtt.Client()
        # self.wait_for_network()
        self.init_mqtt_client()
        self.led.set_color((255, 0, 0))
        self.led.turn_on()

        self.previous_payload = {}
        self.inputs: dict[int, bool] = {}
        self.reset_input_dict()
        self.first_cycle = True

    def callback(self, client, userdata, msg):
        payload = msg.payload.decode()
        topic = msg.topic

        if self.previous_payload.get(topic) == "1" and payload == "0":
            if topic == "Pico1/Eingabe":
                self.logger.debug("Encoder dreht sich")
                self.inputs[1] = True
            elif topic == "Pico2/Eingabe":
                self.logger.debug("Button Pressed")
                self.inputs[2] = True
            elif topic == "Pico3/Eingabe":
                self.logger.debug("Fan spinning")
                self.inputs[3] = True
            elif topic == "Pico4/Eingabe":
                self.logger.debug("Controller geschüttelt")
                self.inputs[4] = True

        # Update the last payload for this topic
        self.previous_payload[topic] = payload

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
                self.logger.info("Connected to MQTT broker.")
            except Exception as _:
                print(f"Connection failed: Retrying in 5 seconds...")
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

    def reset_input_dict(self):
        self.inputs = {1: False, 2: False, 3: False, 4: False}


class EasyMode(GenericGamemode):
    def __init__(self, pi):
        super().__init__("Easy Mode", pi)

    def run_gameloop(self):
        if self.first_cycle:
            self.intro()

        input_detected = False
        for key in self.inputs:
            if self.inputs[key]:
                input_detected = True
        if input_detected:
            self.reset_input_dict()
            self.led.set_color((0, 255, 0))
            self.pump.open()
            self.led.sinus(period=0.33, cycles=3)
            self.pump.close()
        else:
            self.led.set_color((255, 0, 0))

    def intro(self):
        self.led.set_color((0, 255, 0))
        self.led.load_bar()
        self.led.set_color((255, 0, 0))
        self.first_cycle = False


class MediumMode(GenericGamemode):
    def __init__(self, pi):
        super().__init__("Medium Mode", pi)

    def run_gameloop(self):
        if self.first_cycle:
            self.intro()

        input_amount = 0
        for key in self.inputs:
            if self.inputs[key]:
                input_amount += 1
        if input_amount > 2:
            self.reset_input_dict()
            self.led.set_color((0, 255, 0))
            self.pump.open()
            self.led.sinus()
            self.pump.close()
        else:
            self.led.set_color((255, 0, 0))

    def intro(self):
        self.led.set_color((0, 0, 255))
        self.led.load_bar()
        self.led.set_color((255, 0, 0))
        self.first_cycle = False


class HardMode(GenericGamemode):
    def __init__(self, pi):
        super().__init__("Hard Mode", pi)
        self.last_player = 0

    def run_gameloop(self):
        if self.first_cycle:
            self.intro()

        random_player = self.choose_random_player()
        self.led.set_color(self.get_color_by_player(random_player))
        time.sleep(2)
        if self.inputs[random_player]:
            self.led.set_color((0, 255, 0))
            self.pump.open()
            self.led.sinus(cycles=5)
            self.pump.close()
            self.reset_input_dict()
        else:
            self.led.set_color((255, 0, 0))
            self.led.sinus()

    def intro(self):
        self.led.set_color((255, 0, 0))
        self.led.load_bar()
        self.first_cycle = False

    def choose_random_player(self) -> int:
        players = [1, 2, 3, 4]
        if self.last_player in players:
            players.remove(self.last_player)
        random_player = random.choice(players)
        self.last_player = random_player
        return random_player

    def get_color_by_player(self, player: int) -> tuple[int, int, int]:
        if player == 1:
            return 255, 255, 0
        elif player == 2:
            return 0, 0, 255
        elif player == 3:
            return 0, 255, 255
        elif player == 4:
            return 255, 0, 255
        else:
            self.logger.warning(f"Player {player} is not matched with a color.")
            raise NotImplementedError
