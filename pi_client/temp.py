import json

import paho.mqtt.client as mqtt
import RPi.GPIO as gpio
import dht11
import time
import datetime


class Temp_Hum:
    def __init__(self, IP="localhost", temperature=0, humidity=0):
        self.IP = IP
        self._client = None
        self.TH_pin = 16
        self.temperature = temperature
        self.humidity = humidity
        self.instance = None

    @property
    def client(self):  # 클라이언트 private로 생성
        if self._client:
            return self._client
        else:
            client = mqtt.Client()

            def on_connect(client, userdata, flags, rc):
                print("Connected Temp/Hum sensor" + str(rc))

            def on_publish(client, userdata, mid):
                msg_id = mid

            client.on_connect = on_connect
            client.on_publish = on_publish
            self._client = client
            return client

    def init_gpio(self):
        gpio.setmode(gpio.BCM)
        gpio.cleanup()
        self.instance = dht11.DHT11(self.TH_pin)

    def get_TH(self):
        res = self.instance.read()
        if res.is_valid():
            self.temperature = res.temperature
            self.humidity = res.humidity

    def run(self):
        self.init_gpio()
        self.client.connect(self.IP)
        self.client.loop_start()
        try:
            while True:
                self.get_TH()
                msg = {
                    "temperature": self.temperature,
                    "humidity": self.humidity
                }
                self.client.publish("sensor/temp_hum", json.dumps(msg))
                print(f"[sensor/temp_hum] publish : {msg}")
                time.sleep(5)
        except KeyboardInterrupt:
            print("Finished temp, hum!")
            self.client.loop_stop()
            self.client.disconnect()
            gpio.cleanup()
