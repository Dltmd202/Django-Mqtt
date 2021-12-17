import paho.mqtt.client as mqtt
import RPi.GPIO as gpio
import time
import json


class Distance:
    def __init__(self, ip="localhost"):
        self.distance = 0
        self.ip = ip
        self._client = None
        self.trig_pin = 20
        self.echo_pin = 21

    @property
    def client(self):
        if self._client:
            return self._client
        else:
            client = mqtt.Client()

            def on_connect(client, userdata, flags, rc):
                print("Connected Ultrasonic sensor" + str(rc))

            def on_publish(client, userdata, mid):
                msg_id = mid

            client.on_connect = on_connect
            client.on_publish = on_publish
            self._client = client
            return client

    def init_gpio(self):
        gpio.setmode(gpio.BCM)
        gpio.setwarnings(False)
        gpio.setup(self.trig_pin, gpio.OUT)
        gpio.setup(self.echo_pin, gpio.IN)

    def get_distance(self):
        gpio.output(self.trig_pin, False)
        time.sleep(1)
        gpio.output(self.trig_pin, True)
        time.sleep(0.00001)
        gpio.output(self.trig_pin, False)
        while gpio.input(self.echo_pin) == 0:
            pulse_start = time.time()
        while gpio.input(self.echo_pin) == 1:
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 34000 / 2
        distance = round(distance, 2)
        return distance

    def run(self):
        self.init_gpio()
        self.client.connect(self.ip)
        self.client.loop_start()
        try:
            while True:
                self.distance = self.get_distance()
                msg = {
                    "distance": self.distance
                }
                self.client.publish("sensor/distance", json.dumps(msg)) 
                print(f"[sensor/distance] publish : {msg}") 
                time.sleep(1)
        except KeyboardInterrupt:
            print("Finished distance!")
            self.client.loop_stop()
            self.client.disconnect()
            gpio.cleanup()


if __name__ == "__main__":
    dis = Distance()
    dis.run()
