import json
import os

import paho.mqtt.client as mqtt
import requests


class ServerApplication:
    TEMP = 30
    HUM = 40
    def __init__(self, ip):
        self.ip = os.environ.get("PI", ip)
        self.client = self.getClient()
        self.is_open = None
        self.is_lock = None
        self.distance = None
        self.is_person = None
        self.open_order = None
        self.temp = None
        self.hum = None
        self.rain = None

    def getClient(self):
        client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            print("connected with result code " + str(rc))
            client.subscribe("sensor/distance")
            client.subscribe("sensor/temp_hum")
            client.subscribe("sensor/detect")
            client.subscribe("sensor/rain")
            client.subscribe("control/motor")
            client.subscribe("control/lock")
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
            elif msg.topic == 'sensor/user':
                self.orderParser(msg)
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
                data=str(data)
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
    
    def orderParser(self, msg):
        order_msg = json.loads(msg.payload)
        self.open_order = order_msg["order"]
    
    def defOpenNLock(self):
        res = {
            "is_open": False,
            "is_lock": False
        }
        if self.distance > 10:
            res["is_open"] = True
            res["is_lock"] = False
            return res
        if self.is_person:
            res["is_open"] = False
            res["is_lock"] = True
        if self.open_order:
            res["is_open"] = False
            res["is_lock"] = True
            return res
        if self.rain:
            res["is_open"] = False
            res["is_lock"] = False
        if TEMP + 10 < self.temp or HUM + 10 < self.hum:
            res["is_open"] = True
            res["is_lock"] = False
        if TEMP - 10 > self.temp or HUM - 10 > self.hum:
            res["is_open"] = False
            res["is_lock"] = False
        else:
            res["is_open"] = True
            res["is_lock"] = False

    def motorControl(self):
        res = self.defOpenNLock()
        lockMsg = {
            "is_lock": res["is_lock"]
        }
        openMsg = {
            "is_open": res["is_open"]
        }
        if res["is_open"] == True:
            self.client.publish("sensor/lock", json.dumps(lockMsg))
            self.client.publish("sendor/moter", json.dumps(openMsg))
        else:
            self.client.publish("sendor/moter", json.dumps(openMsg))
            self.client.publish("sensor/lock", json.dumps(lockMsg))

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
            "is_open": self.is_open if self.is_open else False,
            "is_lock": self.is_lock if self.is_lock else False
        }
        return json.dumps(data)


if __name__ == '__main__':
    service = ServerApplication(os.environ.get("PI", "localhost"))
    service.run()
