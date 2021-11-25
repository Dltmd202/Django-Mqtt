import time
import paho.mqtt.client as mqtt
import RPi.GPIO as gpio
import json

class PIR:
    def __init__(self, detected=False, IP="localhost"):
        self._client = None
        self.detected = detected  # 외부 사람감지
        self.IP = IP
        self.pir_pin = 17

    @property
    def client(self):
        if self.client:
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
        gpio.setup(self.pir_Pin, gpio.IN)

    def run(self):
        self.init_gpio()
        self.client.connect(self.IP)
        self.client.loop_start()
        try:
            while True:
                self.detected = gpio.input(self.pir_pin)
                msg = {
                    "detected": self.detected
                }
                self.client.publish("sensor/pir", json.dumps(msg))
                print(f"publishing : {msg}")
                time.sleep(1)
        except KeyboardInterrupt:
            print("Finished")
            self.client.loop_stop()
            self.client.disconnect()
            gpio.cleanup()


if __name__ == "__main__":
    sensor_pir = PIR()
    sensor_pir.run()