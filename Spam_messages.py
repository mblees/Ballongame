import time
import paho.mqtt.client as mqtt

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username="PicoNet", password="geheimespasswort")
mqtt_client.connect("192.168.0.127", 1883, 60)

while True:
    mqtt_client.publish("Pico1/Eingabe", "0")
    mqtt_client.publish("Pico2/Eingabe", "0")
    mqtt_client.publish("Pico3/Eingabe", "0")
    mqtt_client.publish("Pico4/Eingabe", "0")
    time.sleep(0.2)
