import json
import os

import paho.mqtt.client as mqtt
import requests

from sms.lib.auth import *
from sms.lib.config import *
import datetime


class ServerApplication:
    def __init__(self, ip):
        self.ip = os.environ.get("PI", ip)
        self.client = self.getClient()
        self.is_open = False
        self.is_lock = False
        self.distance = 0
        self.is_person = None
        self.open_order = None
        self.temp = 0
        self.hum = 0
        self.rain = None
        self.temp_default = 23.0
        self.hum_default = 40.0
        self.sms = False
        self.time = None

    def getClient(self):
        client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            print("connected with result code " + str(rc))
            client.subscribe("sensor/distance")
            client.subscribe("sensor/temp_hum")
            client.subscribe("sensor/detect")
            client.subscribe("sensor/rain")
            client.subscribe("sensor/user")
            client.subscribe("sensor/wish")

        def on_message(client, userdata, msg):
            if msg.topic == 'sensor/distance':
                self.distanceParser(msg)
            if msg.topic == 'sensor/temp_hum':
                self.tempParser(msg)
            if msg.topic == 'sensor/detect':
                self.detectParser(msg)
            if msg.topic == 'sensor/rain':
                self.rainParser(msg)
            if msg.topic == 'sensor/user':
                self.orderParser(msg)
            if msg.topic == 'sensor/wish':
                self.wishParser(msg)
            print(f"[{msg.topic}] sub : {msg.payload}")
            self.motorControl()
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
            }
            data = self.get_data()
            res = requests.patch(
                "http://172.20.10.7:8000/window/inf/1/?format=json",
                headers=headers,
                data=str(data)
            )
            res = requests.get(
                "http://172.20.10.7:8000/window/inf/1/?format=json"
            )

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
        detct_msg = json.loads(msg.payload)
        self.is_person = detct_msg['detected']

    def rainParser(self, msg):
        rain_msg = json.loads(msg.payload)
        self.rain = msg.payload
    
    def orderParser(self, msg):
        order_msg = json.loads(msg.payload)
        self.open_order = order_msg["order"]    
        
    def wishParser(self, msg):
        print(msg.payload)
        wish = json.loads(msg.payload)
        self.temp_default = float(wish["wishTemperature"])
        self.hum_default = float(wish['wishHum'])

    def sendSms(self):
        sms = {
            'message': {
                'to': '01087654321',
                'from': '01012345678',
                'text': f'현재 스마트 창문이 침입자를 감지하여 창문을 닫았습니다.'
            }
        }
        res = requests.post(getUrl('/messages/v4/send'),
                            headers=get_headers(apiKey, apiSecret), json=sms)
        print(json.dumps(json.loads(res.text), indent=2, ensure_ascii=False))
   
    def defOpenNLock(self):
        res = {
            "is_open": self.is_open,
            "is_lock": self.is_lock
        }
        # if self.distance > 10 and not self.is_open:
        #     print("문이 정보와 달라 여는 중!!!!!!!!!!!!!!!")
        #     res["is_open"] = True
        #     res["is_lock"] = False
        #     return res
        # if self.distance <= 10 and self.is_open:
        #     print("문이 정보와 달라 닫는 중!!!!!!!!!!!!!!!")
        #     res["is_open"] = False
        #     res["is_lock"] = False
        #     return res
        if self.is_person:
            print("외부 접근으로 인해 닫는 중@@@@@@@@@@@@@@@@")
            res["is_open"] = False
            res["is_lock"] = True
            if not self.sms:
                self.sendSms()
                self.sms = True
            return res
        if self.open_order is not None:
            print(self.open_order)
            if self.open_order:
                print("명령으로 인해 여는 중###########")
                res["is_open"] = True
                res["is_lock"] = False
            if not self.open_order:
                print("명령으로 인해 닫는 중###########")
                res["is_open"] = False
                res["is_lock"] = False
            self.open_order = None
            return res
        if self.rain:
            print("우천으로 인해 닫는 중$$$$$$$$$$$$$$")
            res["is_open"] = False
            res["is_lock"] = False
            return res
        if self.temp_default + 5 < self.temp:
            print("사용자 온도 정보로 인해 여는 중%%%%%%%%%%%%%%%%")
            res["is_open"] = True
            res["is_lock"] = False
            return res
        if self.hum_default + 5 < self.hum:
            print("사용자 습도 정보로 인해 여는 중%%%%%%%%%%%%%%%%")
            res["is_open"] = True
            res["is_lock"] = False
            return res
        if self.temp_default - 5 > self.temp:
            print("사용자 온도 정보로 인해 닫는 중%%%%%%%%%%%%%%%%")
            res["is_open"] = False
            res["is_lock"] = False
            return res
        if self.hum_default - 5 > self.hum:
            print("사용자 습도 정보로 인해 닫는 중%%%%%%%%%%%%%%%%")
            res["is_open"] = False
            res["is_lock"] = False
            return res

        now = datetime.datetime.now()
        if self.time is None:
            self.time = now
            print("환기 시작%%%%%%%%%%%%%%%%")
            res["is_open"] = True
            res["is_lock"] = False
        else:
            date_diff = now - self.time
            if (date_diff.seconds/60) >= 60:
                print("환기 종료%%%%%%%%%%%%%%%%")
                res["is_open"] = False
                res["is_lock"] = False
                self.time = None
        return res

    def motorControl(self):
        res = self.defOpenNLock()
        lockMsg = {
            "is_lock": res["is_lock"]
        }
        openMsg = {
            "is_open": res["is_open"]
        }
        if res["is_open"] != self.is_open:
            self.client.publish("control/moter", json.dumps(openMsg))
            self.is_open = res["is_open"]
            self.is_lock = res["is_lock"]
        if res["is_lock"] != self.is_lock:
            self.client.publish("control/lock", json.dumps(lockMsg))
            self.is_open = res["is_open"]
            self.is_lock = res["is_lock"]

    def run(self):
        self.client.connect(self.ip)
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
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
            "is_rain": True if self.rain else False,
            "is_open": self.is_open if self.is_open else False,
            "is_lock": self.is_lock if self.is_lock else False,
        }
        return json.dumps(data)


if __name__ == '__main__':
    service = ServerApplication(os.environ.get("PI", "localhost"))
    service.run()
