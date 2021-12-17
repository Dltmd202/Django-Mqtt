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
        self.temp_default = 30
        self.hum_default = 50
        self.time = datetime.datetime.now()

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
            print(f"[{msg.topic}] sub : {msg.payload}")
            self.motorControl()
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
            }
            data = self.get_data()
            res = requests.put(
                "http://172.20.10.7:8000/window/inf/1/?format=json",
                headers=headers,
                data=str(data)
            )
            res = requests.get(
                "http://172.20.10.7:8000/window/inf/1/?format=json"
            )
            time.sleep(3)

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
        self.rain = True if rain_msg['rainlevel'] > 0 else False
    
    def orderParser(self, msg):
        order_msg = json.loads(msg.payload)
        self.open_order = order_msg["order"]

    def sendSms(self):
        sms = {
            'message': {
                'to': '01034657095',
                'from': '01037065337',
                'text': f'현재 스마트 창문이 침입자를 감지하여 창문을 닫았습니다.'
            }
        }
        res = requests.post(getUrl('/messages/v4/send'),
                            headers=get_headers(apiKey, apiSecret), json=sms)
        print(json.dumps(json.loads(res.text), indent=2, ensure_ascii=False))
   
    def defOpenNLock(self):
        res = {
            "is_open": False,
            "is_lock": False
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
        print("is_person", self.is_person)
        if self.is_person:
            print("외부 접근으로 인해 닫는 중@@@@@@@@@@@@@@@@")
            res["is_open"] = False
            res["is_lock"] = True
            #self.sendSms()
            return res
        # if self.open_order is not None:
        #     print(self.open_order)
        #     if self.open_order:
        #         print("명령으로 인해 여는 중###########")
        #         res["is_open"] = True
        #         res["is_lock"] = False
        #     if not self.open_order:
        #         print("명령으로 인해 닫는 중###########")
        #         res["is_open"] = False
        #         res["is_lock"] = False
        #     self.open_order = None
        #     return res
        # if self.rain:
        #     print("우천으로 인해 닫는 중$$$$$$$$$$$$$$")
        #     res["is_open"] = False
        #     res["is_lock"] = False
        #     return res
        # if self.temp_default + 10 < self.temp or self.hum_default + 10 < self.hum:
        #     print("사용자 설정 정보로 인해 여는 중%%%%%%%%%%%%%%%%")
        #     res["is_open"] = True
        #     res["is_lock"] = False
        #     return res
        # elif self.temp_default - 10 > self.temp or self.hum_default - 10 > self.hum:
        #     print("사용자 설정 정보로 인해 닫는 중%%%%%%%%%%%%%%%%")
        #     res["is_open"] = False
        #     res["is_lock"] = False
        #     return res
        else:
            self.time = datetime.datetime.now()
            print("환기 중%%%%%%%%%%%%%%%%")
            res["is_open"] = True
            res["is_lock"] = False
            return res

    def motorControl(self):
        res = self.defOpenNLock()
        lockMsg = {
            "is_lock": res["is_lock"]
        }
        openMsg = {
            "is_open": res["is_open"]
        }
        #if res["is_open"] != self.is_open:
            # now = datetime.datetime.now()
            # if self.time + datetime.timedelta(minutes=1) < now:
            #     self.time = now
        self.client.publish("control/moter", json.dumps(openMsg))
            # self.is_open = res["is_open"]
            # self.is_lock = res["is_lock"]
            
       # if res["is_lock"] != self.is_lock:
            #if not self.is_open:
                # now = datetime.datetime.now()
                # if self.time + datetime.timedelta(minutes=1) < now:
                #     self.time = now
        self.client.publish("control/lock", json.dumps(lockMsg))
            # self.is_open = res["is_open"]
            # self.is_lock = res["is_lock"]

        # if res["is_open"] == True:
        #     print("msg = ", lockMsg, openMsg)
        #     self.client.publish("control/lock", json.dumps(lockMsg))
        #     self.client.publish("control/moter", json.dumps(openMsg))
        # else:
        #     print("msg = ", lockMsg, openMsg)
        #     self.client.publish("control/moter", json.dumps(openMsg))
        #     self.client.publish("control/lock", json.dumps(lockMsg))

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
            "is_rain": self.rain if self.rain else False,
            "is_open": self.is_open if self.is_open else False,
            "is_lock": self.is_lock if self.is_lock else False,
        }
        return json.dumps(data)


if __name__ == '__main__':
    service = ServerApplication(os.environ.get("PI", "localhost"))
    service.run()
