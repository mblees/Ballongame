import logging
from src.Hardware import Pump, ReleaseValve, LED, MiuzeiDigitalServo, Button
import paho.mqtt.client as mqtt
import time
import random

class GamemodeTools:
    def __init__(self, pi):
        self.logger = logging.getLogger("GamemodeTools")
        self.logger.info("Initializing GamemodeTools")
        
        self.pi = pi
        self.pump = Pump(self.pi)
        self.releaseValve = ReleaseValve(self.pi)
        self.led = LED(self.pi, num_leds=75)
        self.servo = MiuzeiDigitalServo(self.pi, 13)
        
        self.led.set_color((255, 0, 0))
        self.led.turn_on()
        
        self.eject_button = Button(self.pi, 26)
        self.eject_button.enable_interrupt(callback=self.servo.eject_and_reset, poll_interval=2)
        
        self.explode_button = Button(self.pi, 16)
        self.explode_button.enable_interrupt(callback=self.toggle_explode_mode, poll_interval=2)
        self.explode = False
        
        self.mqtt_client = mqtt.Client()
        self.init_mqtt_client()
        self.previous_payload = {}
        self.inputs: dict[int, bool] = {}
        
        self.pi.write(6, 1)
        
    def callback(self, client, userdata, msg):
        payload = msg.payload.decode()
        topic = msg.topic

        if self.previous_payload.get(topic) == "1" and payload == "0":
            if topic == "Pico2/Eingabe":
                self.logger.debug("Input from Player 2 detected.")
                self.inputs[2] = True

        if payload == "0":
            if topic == "Pico1/Eingabe":
                self.logger.debug("Input from Player 1 detected.")
                self.inputs[1] = True
            elif topic == "Pico3/Eingabe":
                self.logger.debug("Input from Player 3 detected.")
                self.inputs[3] = True
            elif topic == "Pico4/Eingabe":
                self.logger.debug("Input from Player 4 detected.")
                self.inputs[4] = True
        
        self.previous_payload[topic] = payload
        
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
        
    def toggle_explode_mode(self):
        if self.explode:
            self.explode = False
            self.logger.debug("Explode mode deactivated")
        else:
            self.explode = True
            self.logger.debug("Explode mode activated")
    
    
class GenericGamemode:
    def __init__(self, logging_name: str, tools: GamemodeTools):
        self.logger = logging.getLogger(logging_name)
        self.mode: str = logging_name
        
        self.tools = tools
        
        self.led = tools.led
        self.pump = tools.pump
        self.releaseValve = tools.releaseValve
        self.servo = tools.servo
        self.servo.reset()

        self.inputs = tools.inputs
        self.previous_payload = tools.previous_payload
        self.reset_input_dict()
        
        self.explode = tools.explode
        
        self.first_cycle = True
        self.won = False
        self.interrupt_active = False
        self.waiting = False


    def run_gameloop(self):
        self.logger.warning("Using generic Gamemode Class. Overwrite this function.")
        raise NotImplementedError()

    def print_mode(self):
        self.logger.info(f"Mode is set to: {str(self.mode)}")

    def reset_input_dict(self):
        self.tools.inputs = {1: False, 2: False, 3: False, 4: False}
        
    def cleanup(self):
        self.logger.info("Cleaning up Gamemode resources...")
        self.pump.close()
        self.releaseValve.close()
        self.led.turn_off()
        self.servo.reset()
        
    def update_variables(self):
        self.inputs = self.tools.inputs
        self.previous_payload = self.tools.previous_payload
        self.explode = self.tools.explode


class EasyMode(GenericGamemode):
    def __init__(self, tools: GamemodeTools):
        super().__init__("Easy Mode", tools)

    def run_gameloop(self):
        self.reset_input_dict()
        self.update_variables()
        if self.first_cycle:
            self.interrupt_active = True
            self.intro()
            self.interrupt_active = False

        if self.interrupt_active:
            self.waiting = True
            return
        self.waiting = False

        input_detected = False
        for key in self.inputs:
            if self.inputs[key]:
                input_detected = True
        if input_detected:
            if self.won:
                self.pump.open_time = 0
                self.releaseValve.open_time = 0
                self.won = False
            self.releaseValve.close()
            self.reset_input_dict()
            self.led.set_color((0, 255, 0))
            self.pump.open()
            self.led.sinus(period=0.33, cycles=3)
            self.pump.close()

            balloon_time = self.pump.open_time - self.releaseValve.open_time / 1.5
            self.logger.debug(f"on-time: {balloon_time}")
            if balloon_time < 0:
                self.pump.open_time = 0
                self.releaseValve.open_time = 0
            if balloon_time > 40 and not self.explode:
                self.servo.eject_and_reset()
                self.won = True
        else:
            self.led.set_color((255, 0, 0))
            self.releaseValve.open()

    def intro(self):
        self.led.set_color((0, 255, 0))
        self.led.load_bar()
        self.led.set_color((255, 0, 0))
        self.first_cycle = False


class MediumMode(GenericGamemode):
    def __init__(self, tools: GamemodeTools):
        super().__init__("Medium Mode", tools)

    def run_gameloop(self):
        self.reset_input_dict()
        self.update_variables()
        if self.first_cycle:
            self.interrupt_active = True
            self.intro()
            self.interrupt_active = False

        if self.interrupt_active:
            self.waiting = True
            return
        self.waiting = False

        input_amount = 0
        for key in self.inputs:
            if self.inputs[key]:
                input_amount += 1
        if input_amount > 2:
            self.releaseValve.close()
            if self.won:
                self.pump.open_time = 0
                self.releaseValve.open_time = 0
                self.won = False
            self.reset_input_dict()
            self.led.set_color((0, 255, 0))
            self.pump.open()
            self.led.sinus()
            self.pump.close()

            balloon_time = self.pump.open_time - self.releaseValve.open_time / 1.5
            self.logger.debug(f"on-time: {balloon_time}")
            if balloon_time < 0:
                self.pump.open_time = 0
                self.releaseValve.open_time = 0
            if balloon_time > 40 and not self.explode:
                self.servo.eject_and_reset()
                self.won = True
        else:
            self.releaseValve.open()
            self.led.set_color((255, 0, 0))

    def intro(self):
        self.led.set_color((0, 0, 255))
        self.led.load_bar()
        self.led.set_color((255, 0, 0))
        self.first_cycle = False


class HardMode(GenericGamemode):
    def __init__(self, tools: GamemodeTools):
        super().__init__("Hard Mode", tools)
        self.last_player = 0

    def run_gameloop(self):
        self.reset_input_dict()
        self.update_variables()
        if self.first_cycle:
            self.interrupt_active = True
            self.intro()
            self.releaseValve.open()
            self.interrupt_active = False

        if self.interrupt_active:
            self.waiting = True
            return
        self.waiting = False

        self.releaseValve.close()

        random_player = self.choose_random_player()
        self.led.set_color(self.get_color_by_player(random_player))
        time.sleep(2)
        if self.inputs[random_player]:
            if self.won:
                self.pump.open_time = 0
                self.releaseValve.open_time = 0
                self.won = False
            self.led.set_color((0, 255, 0))
            self.pump.open()
            self.led.sinus(cycles=5)
            self.pump.close()
            self.reset_input_dict()

            balloon_time = self.pump.open_time - self.releaseValve.open_time / 1.5
            self.logger.debug(f"on-time: {balloon_time}")
            if balloon_time < 0:
                self.pump.open_time = 0
                self.releaseValve.open_time = 0
            if balloon_time > 40 and not self.explode:
                self.servo.eject_and_reset()
                self.won = True
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
