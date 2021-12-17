import time
import paho.mqtt.client as mqtt
import RPi.GPIO as gpio
import json


class PIR:
    def __init__(self, ip="localhost"):
        self._client = None
        self.detected = False
        self.ip = ip
        self.pir_pin = 17

    @property
    def client(self):
        if self._client:
            return self._client
        else:
            client = mqtt.Client()
            def on_connect(client, userdata, flags, rc):
                print("Connected PIR Sensor" + str(rc))

            def on_publish(client, userdata, mid):
                msg_id = mid

            client.on_connect = on_connect
            client.on_publish = on_publish
            self._client = client
            return client

    def init_gpio(self):
        gpio.setmode(gpio.BCM)
        gpio.cleanup()
        gpio.setup(self.pir_pin, gpio.IN)

    def run(self):
        self.init_gpio()
        self.client.connect(self.ip)
        self.client.loop_start()
        try:
            while True:
                self.detected = True if gpio.input(self.pir_pin) else False 
                msg = json.dumps({
                    "detected": self.detected,
                    "msg": "fuck you"
                })
                self.client.publish("sensor/detect", msg)
                print(f"[sensor/detect] publish: {msg}")
                time.sleep(1)
        except KeyboardInterrupt:
            print("Finished detected")
            self.client.loop_stop()
            self.client.disconnect()
            gpio.cleanup()


if __name__ == "__main__":
    pir = PIR()
    pir.run()
    