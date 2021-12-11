import json
import os

import paho.mqtt.client as mqtt
import requests


class ServerApplication:
    def __init__(self, ip):
        self.ip = os.environ.get("PI", ip)
        self.client = self.getClient()
        self.status = None
        self.distance = None
        self.is_person = None
        self.temp = None
        self.hum = None
        self.rain = None

    def getClient(self):
        client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            print("connected with result code " + str(rc))
            client.subscribe("sensor/distance")
            client.subscribe("sensor/temp")
            client.subscribe("sensor/detect")
            client.subscribe("sensor/rain")
            client.subscribe("control/motor")
            client.subscribe("sensor/user")

        def on_message(client, userdata, msg):
            print(f"[{msg.topic}] Get Message: {msg.payload}")
            if msg.topic == 'sensor/distance':
                self.distanceParser(msg)
            elif msg.topic == 'sensor/temp_hum':
                self.tempParser(msg)
            elif msg.topic == 'sensor/detect':
                self.detectParser(msg)
            elif msg.topic == 'sensor/rain':
                self.rainParser(msg)
            self.motorControl()
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
            }
            data = self.get_data()
            print(f"publising {data}")
            res = requests.put(
                "http://172.20.10.7:8000/window/inf/1/?format=json",
                headers=headers,
                data=json.dumps(data)
            )
            res = requests.get(
                "http://172.20.10.7:8000/window/inf/1/?format=json"
            )
            print(res.status_code)

        client.on_connect = on_connect
        client.on_message = on_message
        return client

    def distanceParser(self, msg):
        dist_msg = json.loads(msg.payload)
        self.distance = float(dist_msg['distance'])

    def tempParser(self, msg):
        temp_msg = json.loads(msg.payload)
        self.temp = float(temp_msg['temperature'])
        self.hum = float(temp_msg['humidity'])

    def detectParser(self, msg):
        temp_msg = json.loads(msg.payload)
        self.is_person = int(temp_msg['detected'])

    def rainParser(self, msg):
        rain_msg = json.loads(msg.payload)
        self.rain = int(rain_msg['rainlevel'])

    def motorControl(self):
        pass

    def run(self):
        self.client.connect(self.ip)
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Finished!")
            self.client.unsubscribe("sensor/#")
            self.client.unsubscribe("control/#")
            self.client.disconnect()

    def get_data(self):
        data = {
            "id": 1,
            "distance": self.distance if self.distance else 0.,
            "temperature": self.temp if self.temp else 0.,
            "humidity": self.hum if self.hum else 0.,
            "is_person": self.is_person if self.is_person else False,
            "is_rain": self.rain if self.rain else False,
        }
        return json.dumps(data)


if __name__ == '__main__':
    service = ServerApplication(os.environ.get("PI", "localhost"))
    service.run()
