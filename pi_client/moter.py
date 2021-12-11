import time

import paho.mqtt.client as mqtt
import RPi.GPIO as gpio
import json


class Window:
    def __init__(self):
        self._client = None
        self.mpin = 18  # servo 모터 핀번호
        self.servo_pwm = None

    @property
    def client(self):
        if self._client:
            return self._client
        else:
            client = mqtt.Client()

            def on_connect(client, userdata, flags, rc):
                print("Connected Window_Control " + str(rc))
                client.subscribe("control/moter")  # "control/led" 토픽 구독

            def on_message(client, userdata, msg):
                print(f"{msg.topic} : {msg.payload}")  # 수신받은 토픽과 메시지내용 출력
                self.control_window(msg)

            client.on_connect = on_connect
            client.on_message = on_message
            self._client = client
            return client

    def init_pin(self):  # gpio핀 세팅
        gpio.setmode(gpio.BCM)
        gpio.setup(self.mpin, gpio.OUT)
        self.servo_pwm = gpio.PWM(self.mpin, 50)
        self.servo_pwm.start(0)

    def control_window(self, msg):
        state = json.loads(msg.payload)
        if state:  # open
            self.servo_pwm.ChangeDutyCycle(12.5)
            time.sleep(0.5)
        else:  # close
            self.servo_pwm.ChangeDutyCycle(2)
            time.sleep(0.5)

    def run(self):
        self.client.connect("localhost")
        self.init_pin()
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Finished!")
            self.client.unsubscribe("control/moter")
            self.client.disconnect()
            gpio.cleanup()


if __name__ == "__main__":
    Moter_Control = Window()
    Moter_Control.run()