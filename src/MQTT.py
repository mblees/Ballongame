import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker, port=1883, username=None, password=None):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.callback = None
        self.topics = []

        if username and password:
            self.client.username_pw_set(username, password)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        self.start()

    def _on_connect(self, client, userdata, flags, rc):
        print("Verbunden mit Code", rc)
        for topic in self.topics:
            client.subscribe(topic)

    def _on_message(self, client, userdata, msg):
        if self.callback:
            self.callback(msg.topic, msg.payload.decode())

    def set_callback(self, callback):
        self.callback = callback

    def subscribe(self, topic):
        self.topics.append(topic)
        self.client.subscribe(topic)  # direkt abonnieren, falls schon verbunden

    def start(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()
